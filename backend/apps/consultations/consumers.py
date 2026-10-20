from urllib.parse import parse_qs
from uuid import UUID
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class ConsultationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        params = parse_qs(self.scope['query_string'].decode())
        self.patient_code = params.get('code', [None])[0]
        self.patient_id = self.scope.get('session', {}).get('patient_id')
        if not self.patient_id or not await self.patient_session_valid():
            await self.close(code=4403)
            return
        self.group_name = f'patient_{self.patient_code}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    @database_sync_to_async
    def patient_session_valid(self):
        from apps.patients.models import Patient
        return Patient.objects.filter(
            id=self.patient_id, code_unique=self.patient_code, est_actif=True
        ).exists()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        # Mettre le medecin en indisponible quand il se deconnecte
        if hasattr(self, 'medecin_id'):
            await self._set_medecin_indisponible(self.medecin_id)

    @database_sync_to_async
    def _set_medecin_disponible_si_libre(self, medecin):
        # Ne pas changer le statut s'il est deja en consultation (occupe)
        if medecin.statut != 'occupe':
            medecin.statut = 'disponible'
            medecin.save()

    @database_sync_to_async
    def _set_medecin_indisponible(self, medecin_id):
        from apps.accounts.models import MedecinProfile
        try:
            medecin = MedecinProfile.objects.get(id=medecin_id)
            # Ne pas changer si en consultation active (laisser termine_consultation gerer)
            if medecin.statut != 'occupe':
                medecin.statut = 'indisponible'
                medecin.save()
        except MedecinProfile.DoesNotExist:
            pass

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            if not isinstance(data, dict):
                raise ValueError('Expected an object')
            if data.get('action') != 'demander_consultation':
                UUID(str(data.get('consultation_id')))
            if data.get('action') == 'chat_message' and (
                not isinstance(data.get('message'), str) or len(data['message']) > 10000
            ):
                raise ValueError('Invalid message')
        except (ValueError, TypeError):
            await self.send(json.dumps({'type': 'error', 'message': 'Requ?te invalide'}))
            return
        action = data.get('action')
        if action == 'demander_consultation':
            await self.handle_demande(data)
        elif action == 'chat_message':
            await self.handle_chat(data)
        elif action == 'alerte_urgente':
            await self.handle_alerte(data)
        elif action == 'webrtc_offer':
            await self.handle_webrtc_signal(data, 'webrtc_offer')
        elif action == 'webrtc_answer':
            await self.handle_webrtc_signal(data, 'webrtc_answer')
        elif action == 'webrtc_ice':
            await self.handle_webrtc_signal(data, 'webrtc_ice')
        elif action == 'patient_joined_live':
            await self.handle_patient_joined(data)
        elif action == 'media_state':
            await self.handle_media_state(data)

    async def handle_demande(self, data):
        patient_code = self.patient_code
        patient = await self.get_patient(patient_code)
        if not patient:
            await self.send(json.dumps({'type': 'error', 'message': 'Patient non trouvé'}))
            return
        consultation = await self.creer_consultation(patient)

        # Vérifier s'il y a au moins un médecin disponible
        medecins_disponibles = await self.get_medecins_disponibles()
        medecin_traitant = await self.get_medecin_traitant(patient)
        mt_disponible = False
        if medecin_traitant:
            mt_disponible = await self.is_medecin_disponible(medecin_traitant)

        if not medecins_disponibles and not mt_disponible:
            # Aucun médecin disponible — informer immédiatement
            await self.send(json.dumps({
                'type': 'consultation_expiree',
                'message': "Aucun médecin n'est disponible actuellement. Veuillez réessayer plus tard."
            }))
            await self.expirer_consultation(consultation)
            return

        if mt_disponible:
            # Notifier UNIQUEMENT le médecin traitant pendant 90 secondes
            await self.notifier_medecin(medecin_traitant.id, consultation, patient, prioritaire=True)
            await self.send(json.dumps({
                'type': 'consultation_en_attente',
                'consultation_id': str(consultation.id),
                'message': "Votre médecin traitant a été notifié en priorité..."
            }))
            # Lancer le délai 90s en tâche de fond (ne bloque PAS le consumer)
            asyncio.ensure_future(self.delayed_notify_all(consultation, patient, medecin_traitant.id))
        else:
            # Pas de médecin traitant disponible — notifier tous directement
            await self.notifier_tous_medecins(consultation, patient)
            await self.send(json.dumps({
                'type': 'consultation_en_attente',
                'consultation_id': str(consultation.id),
                'message': "Demande envoyée, en attente d'un médecin..."
            }))

    async def handle_chat(self, data):
        consultation_id = data.get('consultation_id')
        message = data.get('message')
        expediteur = 'patient'
        await self.sauvegarder_message(consultation_id, message, expediteur)
        consultation = await self.get_consultation(consultation_id)
        if consultation:
            medecin_id = await self.get_medecin_id(consultation)
            if medecin_id:
                await self.channel_layer.group_send(
                    f'medecin_{medecin_id}',
                    {'type': 'chat_message', 'message': message, 'expediteur': expediteur, 'consultation_id': consultation_id}
                )

    async def handle_alerte(self, data):
        consultation_id = data.get('consultation_id')
        consultation = await self.get_consultation(consultation_id)
        if consultation:
            medecin_id = await self.get_medecin_id(consultation)
            if medecin_id:
                await self.channel_layer.group_send(
                    f'medecin_{medecin_id}',
                    {'type': 'alerte_urgente', 'consultation_id': consultation_id, 'patient_nom': '', 'message': 'Alerte urgente'}
                )

    async def handle_webrtc_signal(self, data, signal_type):
        consultation_id = data.get('consultation_id')
        consultation = await self.get_consultation(consultation_id)
        if consultation:
            medecin_id = await self.get_medecin_id(consultation)
            if medecin_id:
                await self.channel_layer.group_send(
                    f'medecin_{medecin_id}',
                    {'type': signal_type, 'data': data.get('data'), 'consultation_id': consultation_id}
                )

    async def handle_patient_joined(self, data):
        consultation_id = data.get('consultation_id')
        consultation = await self.get_consultation(consultation_id)
        if consultation:
            medecin_id = await self.get_medecin_id(consultation)
            if medecin_id:
                await self.channel_layer.group_send(
                    f'medecin_{medecin_id}',
                    {'type': 'patient_joined_live', 'consultation_id': consultation_id}
                )

    async def handle_media_state(self, data):
        consultation_id = data.get('consultation_id')
        consultation = await self.get_consultation(consultation_id)
        if consultation:
            medecin_id = await self.get_medecin_id(consultation)
            if medecin_id:
                await self.channel_layer.group_send(
                    f'medecin_{medecin_id}',
                    {'type': 'media_state', 'audio': data.get('audio'), 'video': data.get('video'), 'from': 'patient'}
                )

    async def delayed_notify_all(self, consultation, patient, exclure_id):
        await asyncio.sleep(90)
        consultation_fresh = await self.get_consultation(str(consultation.id))
        if consultation_fresh and consultation_fresh.statut == 'en_attente':
            await self.notifier_tous_medecins(consultation, patient, exclure_id=exclure_id)
            try:
                await self.send(json.dumps({
                    'type': 'consultation_en_attente',
                    'consultation_id': str(consultation.id),
                    'message': "Tous les médecins disponibles ont été notifiés..."
                }))
            except:
                pass

    async def notifier_medecin(self, medecin_id, consultation, patient, prioritaire=False):
        await self.channel_layer.group_send(
            f'medecin_{medecin_id}',
            {'type': 'nouvelle_demande', 'consultation_id': str(consultation.id), 'patient_nom': str(patient), 'patient_code': patient.code_unique, 'prioritaire': prioritaire}
        )

    async def notifier_tous_medecins(self, consultation, patient, exclure_id=None):
        medecins = await self.get_medecins_disponibles()
        for medecin in medecins:
            if exclure_id and medecin.id == exclure_id:
                continue
            await self.notifier_medecin(medecin.id, consultation, patient, prioritaire=False)

    # === Event handlers ===
    async def consultation_acceptee(self, event):
        await self.send(json.dumps({'type': 'consultation_acceptee', 'medecin_nom': event['medecin_nom'], 'consultation_id': event['consultation_id']}))

    async def consultation_expiree(self, event):
        await self.send(json.dumps({'type': 'consultation_expiree', 'message': 'Aucun médecin disponible.'}))

    async def capteur_controle(self, event):
        await self.send(json.dumps({'type': 'capteur_controle', 'capteur': event.get('capteur'), 'actif': event.get('actif')}))

    async def consultation_preparation(self, event):
        await self.send(json.dumps({'type': 'consultation_preparation', 'message': event.get('message', ''), 'avec_ordonnance': event.get('avec_ordonnance', False)}))

    async def consultation_cloturee(self, event):
        await self.send(json.dumps({'type': 'consultation_cloturee', 'message': event.get('message', 'Consultation terminée'), 'ordonnance_id': event.get('ordonnance_id')}))

    async def chat_message(self, event):
        await self.send(json.dumps({'type': 'chat_message', 'message': event['message'], 'expediteur': event['expediteur']}))

    async def alerte_urgente(self, event):
        await self.send(json.dumps({'type': 'alerte_urgente'}))

    async def signe_vital(self, event):
        await self.send(json.dumps({'type': 'signe_vital', 'spo2': event.get('spo2'), 'frequence_cardiaque': event.get('frequence_cardiaque'), 'temperature': event.get('temperature'), 'qualite': event.get('qualite')}))

    async def media_state(self, event):
        await self.send(json.dumps({'type': 'media_state', 'audio': event.get('audio'), 'video': event.get('video'), 'from': event.get('from')}))

    async def webrtc_offer(self, event):
        await self.send(json.dumps({'type': 'webrtc_offer', 'data': event['data']}))

    async def webrtc_answer(self, event):
        await self.send(json.dumps({'type': 'webrtc_answer', 'data': event['data']}))

    async def webrtc_ice(self, event):
        await self.send(json.dumps({'type': 'webrtc_ice', 'data': event['data']}))

    async def patient_joined_live(self, event):
        await self.send(json.dumps({'type': 'patient_joined_live', 'consultation_id': event['consultation_id']}))

    # === Database helpers ===
    @database_sync_to_async
    def get_patient(self, code):
        from apps.patients.models import Patient
        try:
            return Patient.objects.get(code_unique=code)
        except Patient.DoesNotExist:
            return None

    @database_sync_to_async
    def creer_consultation(self, patient):
        from apps.consultations.models import Consultation
        import uuid
        return Consultation.objects.create(patient=patient, room_name=str(uuid.uuid4()), statut='en_attente')

    @database_sync_to_async
    def get_consultation(self, consultation_id):
        from apps.consultations.models import Consultation
        try:
            return Consultation.objects.select_related('medecin').get(id=consultation_id, patient_id=self.patient_id)
        except Consultation.DoesNotExist:
            return None

    @database_sync_to_async
    def get_medecin_id(self, consultation):
        return consultation.medecin_id if consultation.medecin else None

    @database_sync_to_async
    def sauvegarder_message(self, consultation_id, contenu, expediteur):
        from apps.messaging.models import Message
        from apps.consultations.models import Consultation
        try:
            consultation = Consultation.objects.get(id=consultation_id, patient_id=self.patient_id)
            Message.objects.create(consultation=consultation, contenu=contenu, expediteur=expediteur, est_alerte_urgente=False)
        except Exception:
            pass

    @database_sync_to_async
    def get_medecin_traitant(self, patient):
        from apps.patients.models import PatientMedecinTraitant
        relation = PatientMedecinTraitant.objects.filter(patient=patient, date_fin__isnull=True).select_related('medecin').first()
        return relation.medecin if relation else None

    @database_sync_to_async
    def is_medecin_disponible(self, medecin):
        return medecin.statut == 'disponible'

    @database_sync_to_async
    def get_medecins_disponibles(self):
        from apps.accounts.models import MedecinProfile
        return list(MedecinProfile.objects.filter(statut='disponible'))

    @database_sync_to_async
    def expirer_consultation(self, consultation):
        consultation.statut = 'expiree'
        consultation.save()


class MedecinConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope['user'].is_authenticated or not self.scope['user'].is_active:
            await self.close()
            return
        from apps.accounts.models import MedecinProfile
        try:
            medecin = await database_sync_to_async(MedecinProfile.objects.get)(user=self.scope['user'])
            self.medecin_id = medecin.id
            self.group_name = f'medecin_{self.medecin_id}'
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            # Mettre le medecin en disponible automatiquement quand il se connecte
            # (sauf s'il etait deja occupe sur une consultation)
            await self._set_medecin_disponible_si_libre(medecin)
            await self.send(json.dumps({'type': 'connected', 'message': 'WebSocket médecin connecté'}))
        except MedecinProfile.DoesNotExist:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        # Mettre le medecin en indisponible quand il se deconnecte
        if hasattr(self, 'medecin_id'):
            await self._set_medecin_indisponible(self.medecin_id)

    @database_sync_to_async
    def _set_medecin_disponible_si_libre(self, medecin):
        # Ne pas changer le statut s'il est deja en consultation (occupe)
        if medecin.statut != 'occupe':
            medecin.statut = 'disponible'
            medecin.save()

    @database_sync_to_async
    def _set_medecin_indisponible(self, medecin_id):
        from apps.accounts.models import MedecinProfile
        try:
            medecin = MedecinProfile.objects.get(id=medecin_id)
            # Ne pas changer si en consultation active (laisser termine_consultation gerer)
            if medecin.statut != 'occupe':
                medecin.statut = 'indisponible'
                medecin.save()
        except MedecinProfile.DoesNotExist:
            pass

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            if not isinstance(data, dict):
                raise ValueError('Expected an object')
            if data.get('action') != 'demander_consultation':
                UUID(str(data.get('consultation_id')))
            if data.get('action') == 'chat_message' and (
                not isinstance(data.get('message'), str) or len(data['message']) > 10000
            ):
                raise ValueError('Invalid message')
        except (ValueError, TypeError):
            await self.send(json.dumps({'type': 'error', 'message': 'Requ?te invalide'}))
            return
        action = data.get('action')
        if action == 'accepter_consultation':
            await self.handle_accepter(data)
        elif action == 'chat_message':
            await self.handle_chat(data)
        elif action == 'webrtc_answer':
            await self.handle_webrtc_signal(data, 'webrtc_answer')
        elif action == 'webrtc_ice':
            await self.handle_webrtc_signal(data, 'webrtc_ice')
        elif action == 'webrtc_offer':
            await self.handle_webrtc_signal(data, 'webrtc_offer')
        elif action == 'media_state':
            await self.handle_media_state(data)

    async def handle_accepter(self, data):
        consultation_id = data.get('consultation_id')
        result = await self.accepter_consultation(consultation_id)
        if result['success']:
            await self.send(json.dumps({'type': 'consultation_acceptee', 'consultation_id': consultation_id, 'patient_nom': result['patient_nom'], 'redirect_url': f'/consultations/{consultation_id}/debriefing/'}))
            await self.channel_layer.group_send(
                f'patient_{result["patient_code"]}',
                {'type': 'consultation_acceptee', 'medecin_nom': result['medecin_nom'], 'consultation_id': consultation_id}
            )
        else:
            await self.send(json.dumps({'type': 'error', 'message': result['message']}))

    async def handle_chat(self, data):
        consultation_id = data.get('consultation_id')
        message = data.get('message')
        expediteur = 'medecin'
        await self.sauvegarder_message(consultation_id, message, expediteur)
        consultation = await self.get_consultation(consultation_id)
        if consultation:
            patient_code = await self.get_patient_code(consultation)
            if patient_code:
                await self.channel_layer.group_send(
                    f'patient_{patient_code}',
                    {'type': 'chat_message', 'message': message, 'expediteur': expediteur, 'consultation_id': consultation_id}
                )

    async def handle_webrtc_signal(self, data, signal_type):
        consultation_id = data.get('consultation_id')
        consultation = await self.get_consultation(consultation_id)
        if consultation:
            patient_code = await self.get_patient_code(consultation)
            if patient_code:
                await self.channel_layer.group_send(
                    f'patient_{patient_code}',
                    {'type': signal_type, 'data': data.get('data'), 'consultation_id': consultation_id}
                )

    async def handle_media_state(self, data):
        consultation_id = data.get('consultation_id')
        consultation = await self.get_consultation(consultation_id)
        if consultation:
            patient_code = await self.get_patient_code(consultation)
            if patient_code:
                await self.channel_layer.group_send(
                    f'patient_{patient_code}',
                    {'type': 'media_state', 'audio': data.get('audio'), 'video': data.get('video'), 'from': 'medecin'}
                )

    # === Event handlers ===
    async def nouvelle_demande(self, event):
        await self.send(json.dumps({'type': 'nouvelle_demande', 'consultation_id': event['consultation_id'], 'patient_nom': event['patient_nom'], 'patient_code': event['patient_code'], 'prioritaire': event['prioritaire']}))

    async def consultation_annulee(self, event):
        await self.send(json.dumps({'type': 'consultation_annulee', 'consultation_id': event['consultation_id']}))

    async def chat_message(self, event):
        await self.send(json.dumps({'type': 'chat_message', 'message': event['message'], 'expediteur': event['expediteur']}))

    async def alerte_urgente(self, event):
        await self.send(json.dumps({'type': 'alerte_urgente', 'patient_nom': event.get('patient_nom', ''), 'message': event.get('message', '')}))

    async def signe_vital(self, event):
        await self.send(json.dumps({'type': 'signe_vital', 'spo2': event.get('spo2'), 'frequence_cardiaque': event.get('frequence_cardiaque'), 'temperature': event.get('temperature'), 'qualite': event.get('qualite')}))

    async def consultation_preparation(self, event):
        await self.send(json.dumps({'type': 'consultation_preparation', 'message': event.get('message', ''), 'avec_ordonnance': event.get('avec_ordonnance', False)}))

    async def consultation_cloturee(self, event):
        await self.send(json.dumps({'type': 'consultation_cloturee', 'message': event.get('message', '')}))

    async def media_state(self, event):
        await self.send(json.dumps({'type': 'media_state', 'audio': event.get('audio'), 'video': event.get('video'), 'from': event.get('from')}))

    async def webrtc_offer(self, event):
        await self.send(json.dumps({'type': 'webrtc_offer', 'data': event['data']}))

    async def webrtc_answer(self, event):
        await self.send(json.dumps({'type': 'webrtc_answer', 'data': event['data']}))

    async def webrtc_ice(self, event):
        await self.send(json.dumps({'type': 'webrtc_ice', 'data': event['data']}))

    async def patient_joined_live(self, event):
        await self.send(json.dumps({'type': 'patient_joined_live', 'consultation_id': event['consultation_id']}))

    # === Database helpers ===
    @database_sync_to_async
    def accepter_consultation(self, consultation_id):
        from apps.consultations.models import Consultation
        from apps.accounts.models import MedecinProfile
        try:
            consultation = Consultation.objects.select_related('patient').get(id=consultation_id, statut='en_attente')
            medecin = MedecinProfile.objects.get(id=self.medecin_id)
            consultation.medecin = medecin
            consultation.statut = 'acceptee'
            consultation.acceptee_le = timezone.now()
            consultation.save()
            medecin.statut = 'occupe'
            medecin.save()
            return {'success': True, 'patient_nom': str(consultation.patient), 'patient_code': consultation.patient.code_unique, 'medecin_nom': str(medecin)}
        except Consultation.DoesNotExist:
            return {'success': False, 'message': 'Consultation déjà prise ou expirée'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    @database_sync_to_async
    def get_consultation(self, consultation_id):
        from apps.consultations.models import Consultation
        try:
            return Consultation.objects.select_related('patient').get(id=consultation_id, medecin_id=self.medecin_id)
        except Consultation.DoesNotExist:
            return None

    @database_sync_to_async
    def get_patient_code(self, consultation):
        return consultation.patient.code_unique if consultation.patient else None

    @database_sync_to_async
    def sauvegarder_message(self, consultation_id, contenu, expediteur):
        from apps.messaging.models import Message
        from apps.consultations.models import Consultation
        try:
            consultation = Consultation.objects.get(id=consultation_id, medecin_id=self.medecin_id)
            Message.objects.create(consultation=consultation, contenu=contenu, expediteur=expediteur, est_alerte_urgente=False)
        except Exception:
            pass

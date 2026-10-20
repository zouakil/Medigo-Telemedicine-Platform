from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from functools import wraps
from secrets import compare_digest
from django.conf import settings
from apps.consultations.permissions import doctor_consultation_required
from .models import SigneVital
from apps.consultations.models import Consultation
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def device_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        expected = settings.SENSOR_API_KEY
        supplied = request.headers.get('X-Sensor-Key', '')
        if not expected or not compare_digest(supplied, expected):
            return JsonResponse({'error': 'Accès non autorisé'}, status=403)
        return view(request, *args, **kwargs)
    return wrapped


@csrf_exempt
@require_http_methods(["POST"])
@device_required
def recevoir_donnees_capteurs(request):
    try:
        data = json.loads(request.body)
        consultation_id = data.get('consultation_id')
        temperature = data.get('temperature')
        spo2 = data.get('spo2')
        frequence_cardiaque = data.get('frequence_cardiaque')
        source = data.get('source', 'combined')
        qualite = data.get('qualite_lecture', 'bon')

        consultation = Consultation.objects.get(id=consultation_id, statut='en_cours')

        SigneVital.objects.create(
            consultation=consultation,
            temperature=temperature,
            spo2=spo2,
            frequence_cardiaque=frequence_cardiaque,
            source=source,
            qualite_lecture=qualite
        )

        channel_layer = get_channel_layer()
        patient_code = consultation.patient.code_unique
        medecin_id = consultation.medecin_id

        payload = {
            'type': 'signe_vital',
            'spo2': spo2,
            'frequence_cardiaque': frequence_cardiaque,
            'temperature': temperature,
            'qualite': qualite,
        }

        async_to_sync(channel_layer.group_send)(f'patient_{patient_code}', payload)
        if medecin_id:
            async_to_sync(channel_layer.group_send)(f'medecin_{medecin_id}', payload)

        return JsonResponse({'status': 'ok'})

    except Consultation.DoesNotExist:
        return JsonResponse({'error': 'Consultation non trouvée'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
@device_required
def get_active_consultation(request):
    try:
        consultation = Consultation.objects.filter(
            statut='en_cours'
        ).select_related('patient').latest('demarree_le')
        return JsonResponse({
            'consultation_id': str(consultation.id),
            'patient_code': consultation.patient.code_unique,
        })
    except Consultation.DoesNotExist:
        return JsonResponse({'consultation_id': None})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@doctor_consultation_required
def controler_capteurs(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
        consultation_id = data.get('consultation_id')
        capteur = data.get('capteur')
        actif = data.get('actif', False)

        from django.core.cache import cache
        cache.set(f'capteur_{consultation_id}_{capteur}', actif, timeout=86400)

        channel_layer = get_channel_layer()
        try:
            consultation = Consultation.objects.get(id=consultation_id)
            patient_code = consultation.patient.code_unique
            async_to_sync(channel_layer.group_send)(
                f'patient_{patient_code}',
                {
                    'type': 'capteur_controle',
                    'capteur': capteur,
                    'actif': actif,
                }
            )
        except Exception as e:
            print(f'Erreur WebSocket capteur: {e}')

        return JsonResponse({'status': 'ok', 'capteur': capteur, 'actif': actif})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@device_required
def get_capteurs_actifs_api(request):
    consultation_id = request.GET.get('consultation_id')
    if not consultation_id:
        return JsonResponse({'spo2': False, 'temperature': False})
    from django.core.cache import cache
    spo2_actif = cache.get(f'capteur_{consultation_id}_spo2', False)
    temp_actif = cache.get(f'capteur_{consultation_id}_temperature', False)
    return JsonResponse({'spo2': spo2_actif, 'temperature': temp_actif})


@require_http_methods(["POST"])
@doctor_consultation_required
def enregistrer_mesures(request):
    try:
        data = json.loads(request.body)
        consultation_id = data.get('consultation_id')
        spo2 = data.get('spo2')
        frequence_cardiaque = data.get('frequence_cardiaque')
        temperature = data.get('temperature')

        consultation = Consultation.objects.get(id=consultation_id)

        signe = SigneVital.objects.create(
            consultation=consultation,
            spo2=spo2 if spo2 and spo2 != '--' else None,
            frequence_cardiaque=frequence_cardiaque if frequence_cardiaque and frequence_cardiaque != '--' else None,
            temperature=temperature if temperature and temperature != '--' else None,
            source='combined',
            qualite_lecture='bon',
            enregistre_par_medecin=True
        )
        return JsonResponse({'status': 'ok', 'id': str(signe.id)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

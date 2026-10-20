from .permissions import doctor_consultation_required
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
from .models import (
    Consultation, ConsultationSymptome, MesureAnthropo,
    PatientMaladie, PatientAllergie, InfoClinique
)
from apps.patients.models import Patient


# ============================================================
# VUES EXISTANTES — NE PAS MODIFIER
# ============================================================

@login_required
@doctor_consultation_required
def sauvegarder_symptomes(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    data = json.loads(request.body)
    consultation_id = data.get('consultation_id')
    symptomes = data.get('symptomes', [])
    try:
        consultation = Consultation.objects.get(id=consultation_id)
        ConsultationSymptome.objects.filter(consultation=consultation).delete()
        for s in symptomes:
            if isinstance(s, dict):
                ConsultationSymptome.objects.create(
                    consultation=consultation,
                    nom_symptome=s.get('nom', ''),
                    intensite=s.get('intensite', 0),
                    evolution=s.get('evolution', 'stable'),
                )
            else:
                ConsultationSymptome.objects.create(
                    consultation=consultation,
                    nom_symptome=s,
                )
        return JsonResponse({'status': 'ok', 'count': len(symptomes)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@doctor_consultation_required
def sauvegarder_mesures(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    data = json.loads(request.body)
    consultation_id = data.get('consultation_id')
    try:
        consultation = Consultation.objects.get(id=consultation_id)
        MesureAnthropo.objects.update_or_create(
            consultation=consultation,
            defaults={
                'taille_cm': data.get('taille_cm'),
                'poids_kg': data.get('poids_kg'),
                'tension_sys': data.get('tension_sys'),
                'tension_dia': data.get('tension_dia'),
                'glycemie': data.get('glycemie'),
            }
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def sauvegarder_infos_patient(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    data = json.loads(request.body)
    patient_id = data.get('patient_id')
    try:
        patient = Patient.objects.filter(id=patient_id, consultations__medecin__user=request.user, consultations__statut__in=['acceptee', 'en_cours']).distinct().get()
        if data.get('groupe_sanguin') is not None:
            patient.groupe_sanguin = data.get('groupe_sanguin')
        patient.save()
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@doctor_consultation_required
def sauvegarder_maladies(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    data = json.loads(request.body)
    consultation_id = data.get('consultation_id')
    maladies = data.get('maladies', [])
    try:
        consultation = Consultation.objects.get(id=consultation_id)
        PatientMaladie.objects.filter(consultation=consultation).delete()
        for m in maladies:
            if isinstance(m, dict):
                PatientMaladie.objects.create(
                    consultation=consultation,
                    nom_maladie=m.get('nom', ''),
                    est_chronique=m.get('est_chronique', False),
                )
            else:
                PatientMaladie.objects.create(
                    consultation=consultation,
                    nom_maladie=m,
                    est_chronique=True,
                )
        return JsonResponse({'status': 'ok', 'count': len(maladies)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@doctor_consultation_required
def sauvegarder_allergies(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    data = json.loads(request.body)
    consultation_id = data.get('consultation_id')
    allergies = data.get('allergies', [])
    try:
        consultation = Consultation.objects.get(id=consultation_id)
        PatientAllergie.objects.filter(consultation=consultation).delete()
        for a in allergies:
            PatientAllergie.objects.create(
                consultation=consultation,
                nom_allergie=a,
            )
        return JsonResponse({'status': 'ok', 'count': len(allergies)})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@doctor_consultation_required
def sauvegarder_info_clinique(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    data = json.loads(request.body)
    consultation_id = data.get('consultation_id')
    try:
        consultation = Consultation.objects.get(id=consultation_id)
        InfoClinique.objects.update_or_create(
            consultation=consultation,
            defaults={
                'tabac': data.get('tabac', 'non_fumeur'),
                'alcool': data.get('alcool', 'jamais'),
                'activite_physique': data.get('activite_physique', 'sedentaire'),
                'enceinte': data.get('enceinte'),
                'maladies_chroniques': data.get('maladies_chroniques', False),
            }
        )
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def check_consultation_active(request):
    from django.http import JsonResponse
    consultation_id = request.GET.get('consultation_id')
    if not consultation_id:
        return JsonResponse({'active': False})
    try:
        c = Consultation.objects.get(id=consultation_id)
        active = c.statut in ['acceptee', 'en_cours'] and c.ended_by is None
        return JsonResponse({'active': active})
    except:
        return JsonResponse({'active': False})


# ============================================================
# NOUVELLES VUES IA MEDIGO
# ============================================================

import logging
logger = logging.getLogger(__name__)


@login_required
def api_medigo_symptomes(request):
    """GET /api/medigo/symptomes/ — Retourne les symptômes canoniques groupés par catégorie."""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        from apps.consultations.services.medigo_ai_service import get_symptomes_canoniques_grouped
        categories = get_symptomes_canoniques_grouped()
        return JsonResponse({'categories': categories})
    except Exception as e:
        logger.exception("Erreur api_medigo_symptomes")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_medigo_maladies(request):
    """GET /api/medigo/maladies/ — Retourne les maladies canoniques avec catégorie et urgence."""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        from apps.consultations.services.medigo_ai_service import get_maladies_canoniques
        maladies = get_maladies_canoniques()
        return JsonResponse({'maladies': maladies})
    except Exception as e:
        logger.exception("Erreur api_medigo_maladies")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@doctor_consultation_required
def api_ia_live(request, consultation_id):
    """GET /api/consultation/<uuid>/ia-live/ — Prédiction IA hybride en temps réel."""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        from apps.consultations.services.medigo_ai_service import predict_live_consultation
        result = predict_live_consultation(consultation_id)
        return JsonResponse(result)
    except Exception as e:
        logger.exception("Erreur api_ia_live pour consultation %s", consultation_id)
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_normalize_symptome(request):
    """POST /api/consultation/normalize-symptome/ — Normalise un symptôme libre vers un canonique."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
        texte = data.get('texte', '')
        if not texte:
            return JsonResponse({'error': 'Champ "texte" requis'}, status=400)

        from apps.consultations.services.medigo_ai_service import normalize_symptom_input
        result = normalize_symptom_input(texte)
        return JsonResponse(result)
    except Exception as e:
        logger.exception("Erreur api_normalize_symptome")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@doctor_consultation_required
def api_patient_summary(request, consultation_id):
    """GET /api/consultation/<uuid>/patient-summary/ — Résumé structuré du patient."""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        consultation = Consultation.objects.select_related('patient').get(id=consultation_id)
        patient = consultation.patient

        # Infos de base
        from datetime import date
        age = 0
        if patient.date_naissance:
            today = date.today()
            age = today.year - patient.date_naissance.year
            if (today.month, today.day) < (patient.date_naissance.month, patient.date_naissance.day):
                age -= 1

        # Antécédents chroniques
        antecedents = list(
            PatientMaladie.objects.filter(
                consultation__patient=patient,
                est_chronique=True
            ).values_list('nom_maladie', flat=True).distinct()
        )

        # Allergies
        allergies = list(
            PatientAllergie.objects.filter(
                consultation__patient=patient
            ).values_list('nom_allergie', flat=True).distinct()
        )

        # Derniers signes vitaux
        from apps.sensors.models import SigneVital
        dernier_signe = SigneVital.objects.filter(
            consultation=consultation
        ).order_by('-mesure_le').first()
        signes_vitaux = None
        if dernier_signe:
            signes_vitaux = {
                'spo2': dernier_signe.spo2,
                'bpm': dernier_signe.frequence_cardiaque,
                'temperature': dernier_signe.temperature,
                'mesure_le': dernier_signe.mesure_le.isoformat() if dernier_signe.mesure_le else None,
            }

        # Mesures anthropo
        mesure = MesureAnthropo.objects.filter(consultation=consultation).last()
        mesures = None
        if mesure:
            mesures = {
                'tension_sys': mesure.tension_sys,
                'tension_dia': mesure.tension_dia,
                'glycemie': mesure.glycemie,
                'taille_cm': mesure.taille_cm,
                'poids_kg': mesure.poids_kg,
            }

        # Info clinique
        info_clinique = None
        try:
            info = InfoClinique.objects.get(consultation=consultation)
            info_clinique = {
                'tabac': info.tabac,
                'alcool': info.alcool,
                'activite_physique': info.activite_physique,
                'enceinte': info.enceinte,
                'maladies_chroniques': info.maladies_chroniques,
            }
        except InfoClinique.DoesNotExist:
            pass

        # Historique des dernières consultations
        historique = list(
            Consultation.objects.filter(
                patient=patient,
                statut='cloturee'
            ).exclude(id=consultation_id).order_by('-cloturee_le')[:5].values(
                'id', 'diagnostic', 'cloturee_le'
            )
        )
        # Convertir les dates pour JSON
        for h in historique:
            if h.get('cloturee_le'):
                h['cloturee_le'] = h['cloturee_le'].isoformat()
            h['id'] = str(h['id'])

        summary = {
            'patient': {
                'nom': patient.nom,
                'prenom': patient.prenom,
                'age': age,
                'sexe': getattr(patient, 'sexe', ''),
                'groupe_sanguin': getattr(patient, 'groupe_sanguin', ''),
            },
            'antecedents_chroniques': antecedents,
            'allergies': allergies,
            'signes_vitaux': signes_vitaux,
            'mesures': mesures,
            'info_clinique': info_clinique,
            'historique_consultations': historique,
        }

        return JsonResponse(summary)
    except Consultation.DoesNotExist:
        return JsonResponse({'error': 'Consultation introuvable'}, status=404)
    except Exception as e:
        logger.exception("Erreur api_patient_summary")
        return JsonResponse({'error': str(e)}, status=500)

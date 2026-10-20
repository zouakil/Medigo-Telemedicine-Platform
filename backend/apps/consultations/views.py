from .permissions import doctor_consultation_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from .models import Consultation, PatientMaladie, MesureAnthropo, PatientAllergie, ConsultationSymptome
from apps.patients.models import Patient, PatientMedecinTraitant
from apps.accounts.models import MedecinProfile
from apps.ordonnances.models import Ordonnance
from apps.consultations.services.rapport_service import generer_rapport_consultation, generer_resume_patient



def nettoyer_consultations_abandonees():
    limite = timezone.now() - timedelta(hours=12)
    abandonnees = Consultation.objects.filter(
        statut__in=['en_cours', 'acceptee'],
        demarree_le__lt=limite
    )
    if abandonnees.exists():
        medecin_ids = list(abandonnees.values_list('medecin_id', flat=True).distinct())
        abandonnees.update(statut='expiree', cloturee_le=timezone.now(), ended_by='systeme')
        MedecinProfile.objects.filter(id__in=medecin_ids, statut='occupe').update(statut='disponible')


def patient_login(request):
    error = None
    if request.method == 'POST':
        code = request.POST.get('code')
        from apps.i18n_patient.translations import get_translation
        lang = request.session.get('patient_lang', 'fr')
        try:
            patient = Patient.objects.get(code_unique=code)
            if not patient.est_actif:
                error = get_translation('access_denied', lang)
            else:
                request.session.cycle_key()
                request.session['patient_id'] = str(patient.id)
                request.session['patient_nom'] = f"{patient.prenom} {patient.nom}"
                return redirect('patient_menu')
        except Patient.DoesNotExist:
            error = get_translation('incorrect_code', lang)
    return render(request, 'patient/login.html', {'error': error})


def patient_menu(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('patient_login')
    patient = get_object_or_404(Patient, id=patient_id)
    # Vérifier s'il y a une consultation active (non clôturée)
    # Exclure celles où le médecin a déjà cliqué clôturer (ended_by est set)
    consultation_active = Consultation.objects.filter(
        patient=patient,
        statut__in=['acceptee', 'en_cours'],
        ended_by__isnull=True
    ).select_related('medecin').order_by('-demandee_le').first()
    return render(request, 'patient/menu.html', {
        'patient': patient,
        'consultation_active': consultation_active,
    })


def patient_consultation(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('patient_login')
    patient = get_object_or_404(Patient, id=patient_id)
    return render(request, 'patient/consultation.html', {'patient': patient})


def patient_logout(request):
    request.session.flush()
    return redirect('patient_login')


def patient_live(request, consultation_id):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('patient_login')
    consultation = get_object_or_404(
        Consultation,
        id=consultation_id,
        patient_id=patient_id
    )
    patient = consultation.patient
    return render(request, 'patient/live.html', {
        'consultation': consultation,
        'patient': patient,
    })


@login_required
def medecin_consultations(request):
    if request.user.role != 'medecin':
        return redirect('admin_dashboard')
    nettoyer_consultations_abandonees()
    medecin = get_object_or_404(MedecinProfile, user=request.user)
    # Filtrer les consultations en attente selon statut médecin et priorité médecin traitant
    from apps.patients.models import PatientMedecinTraitant
    now = timezone.now()
    all_en_attente = Consultation.objects.filter(
        statut='en_attente'
    ).select_related('patient').order_by('-demandee_le')
    consultations_en_attente = []
    if medecin.statut != 'indisponible':
        for c in all_en_attente:
            age_seconds = (now - c.demandee_le).total_seconds()
            if age_seconds < 90:
                mt_rel = PatientMedecinTraitant.objects.filter(patient=c.patient, date_fin__isnull=True).first()
                if mt_rel and mt_rel.medecin_id != medecin.id:
                    if mt_rel.medecin.statut == 'disponible':
                        continue
            consultations_en_attente.append(c)
    mes_consultations = Consultation.objects.filter(
        medecin=medecin
    ).select_related('patient').order_by('-demandee_le')[:10]
    now = timezone.now()
    consultations_avec_countdown = []
    for c in mes_consultations:
        countdown_seconds = None
        if c.statut in ['en_cours', 'acceptee'] and c.demarree_le:
            expiry = c.demarree_le + timedelta(hours=12)
            remaining = (expiry - now).total_seconds()
            countdown_seconds = max(0, int(remaining))
        consultations_avec_countdown.append({
            'consultation': c,
            'countdown_seconds': countdown_seconds,
        })
    return render(request, 'medecin/consultations.html', {
        'medecin': medecin,
        'consultations_en_attente': consultations_en_attente,
        'mes_consultations': mes_consultations,
        'consultations_avec_countdown': consultations_avec_countdown,
    })


@login_required
def debriefing(request, consultation_id):
    if request.user.role != 'medecin':
        return redirect('admin_dashboard')
    medecin = get_object_or_404(MedecinProfile, user=request.user)
    consultation = get_object_or_404(Consultation, id=consultation_id, medecin=medecin)
    patient = consultation.patient
    historique = Consultation.objects.filter(
        patient=patient,
        statut='cloturee'
    ).order_by('-cloturee_le')[:5]

    # Ajouter les maladies à chaque consultation de l'historique
    for h in historique:
        h.maladies_list = list(
            PatientMaladie.objects.filter(consultation=h)
            .values_list('nom_maladie', flat=True)
        )
    maladies = PatientMaladie.objects.filter(
        consultation__patient=patient
    ).select_related('consultation').order_by('-diagnostiquee_le')
    ordonnances = Ordonnance.objects.filter(
        consultation__patient=patient
    ).order_by('-creee_le')[:5]
    from apps.sensors.models import SigneVital
    derniers_signes = SigneVital.objects.filter(
        consultation__patient=patient
    ).order_by('-mesure_le')[:10]
    # Générer le rapport de consultation et résumé patient (100% local)
    rapport = generer_rapport_consultation(consultation)
    resume = generer_resume_patient(patient)

    return render(request, 'medecin/debriefing.html', {
        'consultation': consultation,
        'patient': patient,
        'historique': historique,
        'maladies': maladies,
        'ordonnances': ordonnances,
        'derniers_signes': derniers_signes,
        'rapport': rapport,
        'resume': resume,
    })


@login_required
def demarrer_consultation(request, consultation_id):
    if request.user.role != 'medecin':
        return redirect('admin_dashboard')
    medecin = get_object_or_404(MedecinProfile, user=request.user)
    consultation = get_object_or_404(Consultation, id=consultation_id, medecin=medecin)
    if consultation.statut == 'acceptee':
        consultation.statut = 'en_cours'
        consultation.demarree_le = timezone.now()
        consultation.save()
    return render(request, 'medecin/consultation_live.html', {
        'consultation': consultation,
        'patient': consultation.patient,
        'medecin': medecin,
    })


@login_required
def cloturer_consultation(request, consultation_id):
    if request.user.role != 'medecin':
        return redirect('admin_dashboard')
    medecin = get_object_or_404(MedecinProfile, user=request.user)
    consultation = get_object_or_404(Consultation, id=consultation_id, medecin=medecin)
    if request.method == 'POST':
        consultation.diagnostic = request.POST.get('diagnostic', '')
        consultation.notes_medecin = request.POST.get('notes_medecin', '')
        consultation.statut = 'cloturee'
        consultation.cloturee_le = timezone.now()
        consultation.ended_by = 'medecin'
        consultation.save()
        medecin.statut = 'disponible'
        medecin.save()
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        channel_layer = get_channel_layer()
        from apps.ordonnances.models import Ordonnance
        ordonnance_id = None
        try:
            ord_obj = Ordonnance.objects.filter(consultation=consultation).first()
            if ord_obj:
                ordonnance_id = str(ord_obj.id)
        except Exception:
            pass
        async_to_sync(channel_layer.group_send)(
            f'patient_{consultation.patient.code_unique}',
            {
                'type': 'consultation_cloturee',
                'message': 'La consultation est terminée',
                'ordonnance_id': ordonnance_id,
            }
        )
        from apps.patients.services.patient import assigner_medecin_traitant
        from apps.patients.models import PatientMedecinTraitant
        traitant_actif = PatientMedecinTraitant.objects.filter(
            patient=consultation.patient,
            date_fin__isnull=True
        ).exists()
        if not traitant_actif:
            assigner_medecin_traitant(consultation.patient, medecin)
        messages.success(request, 'Consultation clôturée avec succès')
        return redirect('medecin_consultations')
    return render(request, 'medecin/cloturer.html', {
        'consultation': consultation,
        'patient': consultation.patient,
    })


def au_secours(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return JsonResponse({'error': 'Non identifié'}, status=401)
    from apps.patients.services.patient import get_medecin_traitant
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    patient = get_object_or_404(Patient, id=patient_id)
    medecin_traitant = get_medecin_traitant(patient)
    channel_layer = get_channel_layer()
    if medecin_traitant:
        async_to_sync(channel_layer.group_send)(
            f'medecin_{medecin_traitant.id}',
            {
                'type': 'alerte_urgente',
                'patient_nom': str(patient),
                'patient_code': patient.code_unique,
                'message': 'AU SECOURS',
            }
        )
        return JsonResponse({'status': 'ok', 'message': 'Alerte envoyée au médecin traitant'})
    else:
        medecins = MedecinProfile.objects.filter(statut='disponible')
        for medecin in medecins:
            async_to_sync(channel_layer.group_send)(
                f'medecin_{medecin.id}',
                {
                    'type': 'alerte_urgente',
                    'patient_nom': str(patient),
                    'patient_code': patient.code_unique,
                    'message': 'AU SECOURS',
                }
            )
        return JsonResponse({'status': 'ok', 'message': 'Alerte envoyée à tous les médecins disponibles'})


def annuler_consultation(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return JsonResponse({'error': 'Non identifié'}, status=401)
    import json
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    data = json.loads(request.body)
    consultation_id = data.get('consultation_id')
    try:
        consultation = Consultation.objects.get(
            id=consultation_id,
            patient_id=patient_id,
            statut='en_attente'
        )
        consultation.statut = 'expiree'
        consultation.cloturee_le = timezone.now()
        consultation.ended_by = 'systeme'
        consultation.save()
        channel_layer = get_channel_layer()
        medecins = MedecinProfile.objects.all()
        for medecin in medecins:
            async_to_sync(channel_layer.group_send)(
                f'medecin_{medecin.id}',
                {
                    'type': 'consultation_annulee',
                    'consultation_id': str(consultation.id),
                }
            )
        return JsonResponse({'status': 'ok'})
    except Consultation.DoesNotExist:
        return JsonResponse({'error': 'Consultation non trouvée'}, status=404)


@login_required
def api_consultations_en_attente(request):
    if request.user.role != 'medecin':
        return JsonResponse({'count': 0, 'consultations': []})
    # Ne pas montrer les demandes si le médecin est indisponible
    medecin = MedecinProfile.objects.get(user=request.user)
    if medecin.statut == 'indisponible':
        return JsonResponse({'count': 0, 'consultations': []})
    from apps.patients.models import PatientMedecinTraitant
    from django.utils import timezone
    import datetime
    consultations_qs = Consultation.objects.filter(
        statut='en_attente'
    ).select_related('patient').order_by('-demandee_le')
    # Filtrer : si la consultation a moins de 90 secondes et que le patient a un médecin traitant,
    # ne la montrer qu'au médecin traitant
    filtered = []
    now = timezone.now()
    for c in consultations_qs:
        age_seconds = (now - c.demandee_le).total_seconds()
        if age_seconds < 90:
            # Vérifier si ce patient a un médecin traitant
            mt_rel = PatientMedecinTraitant.objects.filter(patient=c.patient, date_fin__isnull=True).first()
            if mt_rel and mt_rel.medecin_id != medecin.id:
                # Vérifier si le médecin traitant est disponible
                if mt_rel.medecin.statut == 'disponible':
                    # MT disponible — ne pas montrer aux autres pendant 90s
                    continue
                # MT indisponible — montrer à tout le monde directement
        filtered.append(c)
    consultations_qs = filtered
    count = len(consultations_qs)
    consultations = []
    for c in consultations_qs:
        consultations.append({
            'id': str(c.id),
            'patient_nom': f"{c.patient.prenom} {c.patient.nom}",
            'demandee_le': c.demandee_le.strftime('%d/%m/%Y %H:%M'),
        })
    return JsonResponse({'count': count, 'consultations': consultations})


def patient_historique(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('patient_login')
    patient = get_object_or_404(Patient, id=patient_id)
    consultations = Consultation.objects.filter(
        patient=patient,
        statut='cloturee'
    ).select_related('medecin').prefetch_related('symptomes', 'maladies').order_by('-cloturee_le')
    return render(request, 'patient/historique.html', {
        'patient': patient,
        'consultations': consultations,
        'active_tab': 'historique',
    })


def patient_signes_vitaux(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('patient_login')
    patient = get_object_or_404(Patient, id=patient_id)
    from apps.sensors.models import SigneVital
    import json
    signes = SigneVital.objects.filter(
        consultation__patient=patient
    ).order_by('-mesure_le')[:50]
    derniere_mesure = signes.first()
    signes_list = list(signes)[::-1]
    labels = json.dumps([s.mesure_le.strftime('%d/%m %H:%M') for s in signes_list])
    spo2_data = json.dumps([float(s.spo2) if s.spo2 else None for s in signes_list])
    temp_data = json.dumps([float(s.temperature) if s.temperature else None for s in signes_list])
    bpm_data = json.dumps([float(s.frequence_cardiaque) if s.frequence_cardiaque else None for s in signes_list])
    return render(request, 'patient/signes_vitaux.html', {
        'patient': patient,
        'derniere_mesure': derniere_mesure,
        'labels': labels,
        'spo2_data': spo2_data,
        'temp_data': temp_data,
        'bpm_data': bpm_data,
        'active_tab': 'vitaux',
    })


@login_required
def voir_consultation(request, consultation_id):
    if request.user.role != 'medecin':
        return redirect('admin_dashboard')
    medecin = get_object_or_404(MedecinProfile, user=request.user)
    consultation = get_object_or_404(Consultation, id=consultation_id, medecin=medecin)
    patient = consultation.patient
    symptomes = ConsultationSymptome.objects.filter(consultation=consultation)
    maladies = PatientMaladie.objects.filter(consultation=consultation)
    from apps.sensors.models import SigneVital
    signes = SigneVital.objects.filter(consultation=consultation, enregistre_par_medecin=True).order_by('-mesure_le')[:10]
    from apps.ordonnances.models import Ordonnance
    ordonnance = Ordonnance.objects.filter(consultation=consultation).first()
    mesures = consultation.mesures_anthropo.first()
    allergies = PatientAllergie.objects.filter(consultation=consultation)
    info_clinique = None
    try:
        info_clinique = consultation.info_clinique
    except:
        pass
    # Générer le rapport de consultation (100% local)
    from apps.consultations.services.rapport_service import generer_rapport_consultation
    rapport = generer_rapport_consultation(consultation)

    # Images médicales partagées pendant la consultation
    from apps.messaging.models import ImageMedicale
    images = ImageMedicale.objects.filter(consultation=consultation).order_by('envoye_le')

    return render(request, 'medecin/voir_consultation.html', {
        'consultation': consultation,
        'patient': patient,
        'symptomes': symptomes,
        'maladies': maladies,
        'signes': signes,
        'ordonnance': ordonnance,
        'mesures': mesures,
        'allergies': allergies,
        'info_clinique': info_clinique,
        'rapport': rapport,
        'images': images,
    })


@login_required
def mes_patients(request):
    if request.user.role != 'medecin':
        return redirect('admin_dashboard')
    medecin = get_object_or_404(MedecinProfile, user=request.user)
    q = request.GET.get('q', '').strip()
    traitants_qs = PatientMedecinTraitant.objects.filter(
        medecin=medecin,
        date_fin__isnull=True
    ).select_related('patient').order_by('-date_debut')
    if q:
        traitants_qs = traitants_qs.filter(
            patient__nom__icontains=q
        ) | traitants_qs.filter(
            patient__prenom__icontains=q
        )
    patients_data = []
    for t in traitants_qs:
        p = t.patient
        derniere = Consultation.objects.filter(
            patient=p, statut='cloturee'
        ).order_by('-cloturee_le').first()
        mesures = None
        if derniere:
            mesures = derniere.mesures_anthropo.first()
        nb_consultations = Consultation.objects.filter(
            patient=p, statut='cloturee'
        ).count()
        patients_data.append({
            'patient': p,
            'derniere_consultation': derniere,
            'mesures': mesures,
            'nb_consultations': nb_consultations,
        })
    return render(request, 'medecin/mes_patients.html', {
        'medecin': medecin,
        'patients_data': patients_data,
        'q': q,
    })


def patient_attente_ordonnance(request, consultation_id):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('patient_login')
    consultation = get_object_or_404(Consultation, id=consultation_id, patient_id=patient_id)
    patient = consultation.patient
    return render(request, 'patient/attente_ordonnance.html', {
        'consultation': consultation,
        'patient': patient,
    })


def patient_consultation_terminee(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('patient_login')
    return render(request, 'patient/consultation_terminee.html')


@login_required
@doctor_consultation_required
def notifier_fin_consultation(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    import json
    data = json.loads(request.body)
    consultation_id = data.get('consultation_id')
    avec_ordonnance = data.get('avec_ordonnance', False)
    consultation = get_object_or_404(Consultation, id=consultation_id)
    # Marquer que le médecin a initié la clôture
    consultation.ended_by = 'medecin'
    consultation.save()
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    channel_layer = get_channel_layer()
    if avec_ordonnance:
        async_to_sync(channel_layer.group_send)(
            f'patient_{consultation.patient.code_unique}',
            {
                'type': 'consultation_preparation',
                'message': 'Le médecin prépare votre ordonnance...',
                'avec_ordonnance': True,
            }
        )
    else:
        async_to_sync(channel_layer.group_send)(
            f'patient_{consultation.patient.code_unique}',
            {
                'type': 'consultation_cloturee',
                'message': 'La consultation est terminée',
                'ordonnance_id': None,
            }
        )
    return JsonResponse({'status': 'ok'})

@login_required
def fiche_patient(request, patient_id):
    if request.user.role != 'medecin':
        return redirect('admin_dashboard')
    medecin = get_object_or_404(MedecinProfile, user=request.user)
    patient = get_object_or_404(Patient, id=patient_id)
    consultations = Consultation.objects.filter(
        patient=patient, medecin=medecin, statut='cloturee'
    ).order_by('-cloturee_le')
    from apps.sensors.models import SigneVital
    derniers_signes = SigneVital.objects.filter(
        consultation__patient=patient
    ).order_by('-mesure_le')[:10]
    mesures = None
    for c in consultations:
        m = c.mesures_anthropo.first()
        if m:
            mesures = m
            break
    # Dernières allergies
    derniere_consultation_avec_allergies = None
    for c in consultations:
        if c.allergies.exists():
            derniere_consultation_avec_allergies = c
            break
    allergies = derniere_consultation_avec_allergies.allergies.all() if derniere_consultation_avec_allergies else []

    # Dernière info clinique
    info_clinique = None
    for c in consultations:
        try:
            info_clinique = c.info_clinique
            break
        except:
            pass

    # Maladies chroniques
    maladies_chroniques = PatientMaladie.objects.filter(
        consultation__patient=patient,
        est_chronique=True
    ).values_list('nom_maladie', flat=True).distinct()

    # Enrichir les consultations avec icônes
    from apps.ordonnances.models import Ordonnance
    from apps.messaging.models import ImageMedicale
    from apps.sensors.models import SigneVital as SV
    consultations_enrichies = []
    for c in consultations:
        c.a_ordonnance = Ordonnance.objects.filter(consultation=c).exists()
        c.a_images = ImageMedicale.objects.filter(consultation=c).exists()
        c.a_mesures = SV.objects.filter(consultation=c).exists()
        c.a_maladies = c.maladies.exists()
        consultations_enrichies.append(c)

    return render(request, 'medecin/fiche_patient.html', {
        'patient': patient,
        'consultations': consultations_enrichies,
        'derniers_signes': derniers_signes,
        'mesures': mesures,
        'allergies': allergies,
        'info_clinique': info_clinique,
        'maladies_chroniques': maladies_chroniques,
    })



# ============================================================
# i18n PATIENT - Gestion de la langue
# ============================================================

def patient_choisir_langue(request):
    """Page d'accueil patient - choix de la langue."""
    # Si la langue est deja choisie ET le patient connecte, aller au menu
    if request.session.get('patient_lang') and request.session.get('patient_id'):
        return redirect('patient_menu')
    # Si la langue est choisie mais pas connecte, aller au login
    if request.session.get('patient_lang'):
        return redirect('patient_login')
    return render(request, 'patient/choisir_langue.html')


def patient_set_lang(request, lang):
    """Définit la langue dans la session et redirige vers le login."""
    if lang in ('fr', 'ar'):
        request.session['patient_lang'] = lang
    # Si deja connecte, retourner au menu
    if request.session.get('patient_id'):
        return redirect('patient_menu')
    return redirect('patient_login')


def patient_change_lang(request, lang):
    """Change la langue à la volée (depuis n'importe quelle page)."""
    if lang in ('fr', 'ar'):
        request.session['patient_lang'] = lang
    # Retour à la page précédente ou au menu
    next_url = request.GET.get('next', '')
    if next_url:
        return redirect(next_url)
    if request.session.get('patient_id'):
        return redirect('patient_menu')
    return redirect('patient_login')

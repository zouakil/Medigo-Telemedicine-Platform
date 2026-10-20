from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
import os
from django.conf import settings
from .models import Ordonnance
from apps.consultations.models import Consultation
from apps.accounts.models import MedecinProfile
from .services.pdf_generator import generer_pdf_ordonnance, generer_qr_code


@login_required
def creer_ordonnance(request, consultation_id):
    if request.user.role != 'medecin':
        return redirect('admin_dashboard')

    medecin = get_object_or_404(MedecinProfile, user=request.user)
    consultation = get_object_or_404(Consultation, id=consultation_id, medecin=medecin)

    if hasattr(consultation, 'ordonnance'):
        messages.warning(request, 'Une ordonnance existe déjà pour cette consultation')
        return redirect('voir_ordonnance', ordonnance_id=consultation.ordonnance.id)

    if request.method == 'POST':
        contenu = request.POST.get('contenu', '').strip()
        if not contenu:
            messages.error(request, 'Le contenu de l\'ordonnance est obligatoire')
            return render(request, 'medecin/creer_ordonnance.html', {
                'consultation': consultation,
                'patient': consultation.patient
            })

        ordonnance = Ordonnance.objects.create(
            consultation=consultation,
            contenu=contenu
        )

        base_url = request.build_absolute_uri('/').rstrip('/')
        generer_pdf_ordonnance(ordonnance)
        generer_qr_code(ordonnance, base_url)

        messages.success(request, 'Ordonnance générée avec succès')
        return redirect('voir_ordonnance', ordonnance_id=ordonnance.id)

    from apps.consultations.models import PatientMaladie, ConsultationSymptome, PatientAllergie, MesureAnthropo
    maladies_list = list(PatientMaladie.objects.filter(consultation=consultation).values_list('nom_maladie', flat=True))
    symptomes_list = list(ConsultationSymptome.objects.filter(consultation=consultation).values_list('nom_symptome', flat=True))
    allergies_list = list(PatientAllergie.objects.filter(consultation=consultation).values_list('nom_allergie', flat=True))
    mesures = MesureAnthropo.objects.filter(consultation=consultation).first()
    info_clinique = None
    try:
        from apps.consultations.models import InfoClinique
        info_clinique = InfoClinique.objects.filter(consultation=consultation).first()
    except:
        pass
    return render(request, 'medecin/creer_ordonnance.html', {
        'consultation': consultation,
        'patient': consultation.patient,
        'maladies_list': maladies_list,
        'symptomes_list': symptomes_list,
        'allergies_list': allergies_list,
        'mesures': mesures,
        'info_clinique': info_clinique,
    })


@login_required
def voir_ordonnance_medecin(request, ordonnance_id):
    if request.user.role != 'medecin':
        return redirect('admin_dashboard')

    ordonnance = get_object_or_404(Ordonnance, id=ordonnance_id, consultation__medecin__user=request.user)
    return render(request, 'medecin/voir_ordonnance.html', {
        'ordonnance': ordonnance,
        'patient': ordonnance.consultation.patient,
    })


def voir_ordonnance_patient(request, ordonnance_id):
    # Vérifier si le patient est déjà connecté
    patient_id = request.session.get('patient_id')
    if patient_id:
        try:
            ordonnance = Ordonnance.objects.get(id=ordonnance_id, consultation__patient_id=patient_id)
            return render(request, 'patient/voir_ordonnance.html', {'ordonnance': ordonnance})
        except Ordonnance.DoesNotExist:
            pass

    # Page de vérification par code patient
    ordonnance = get_object_or_404(Ordonnance, id=ordonnance_id)
    error = None

    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        if code == ordonnance.consultation.patient.code_unique:
            return render(request, 'patient/voir_ordonnance.html', {'ordonnance': ordonnance, 'verified_code': code})
        else:
            error = "Code patient incorrect. Accès non autorisé."

    return render(request, 'patient/verifier_ordonnance.html', {
        'ordonnance_id': ordonnance_id,
        'error': error,
    })

def telecharger_pdf(request, ordonnance_id):
    patient_id = request.session.get('patient_id')
    user = request.user
    code_verifie = request.GET.get('code', '')
    ordonnance = get_object_or_404(Ordonnance, id=ordonnance_id)

    # Autoriser si : patient connecté, médecin connecté, ou code patient correct
    autorise = False
    if patient_id == str(ordonnance.consultation.patient_id):
        autorise = True
    elif (user.is_authenticated and user.is_active and user.role == 'medecin'
          and ordonnance.consultation.medecin.user_id == user.id):
        autorise = True
    elif code_verifie == ordonnance.consultation.patient.code_unique:
        autorise = True

    if not autorise:
        return render(request, 'patient/verifier_ordonnance.html', {
            'ordonnance_id': ordonnance_id,
            'error': 'Accès non autorisé. Veuillez vérifier votre code patient.',
        })

    filepath = os.path.join(settings.MEDIA_ROOT, ordonnance.storage_key)
    if not os.path.exists(filepath):
        raise Http404
    return FileResponse(
        open(filepath, 'rb'),
        content_type='application/pdf',
        as_attachment=True,
        filename=f"ordonnance_{ordonnance.consultation.patient.nom}.pdf"
    )

def liste_ordonnances_patient(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('patient_login')

    from apps.patients.models import Patient
    patient = get_object_or_404(Patient, id=patient_id)
    ordonnances = Ordonnance.objects.filter(
        consultation__patient=patient
    ).select_related('consultation__medecin').order_by('-creee_le')

    return render(request, 'patient/ordonnances.html', {
        'patient': patient,
        'ordonnances': ordonnances,
    })

def api_recherche_medicaments(request):
    from django.http import JsonResponse
    from .models import Medicament
    from django.db.models import Q
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})
    meds = Medicament.objects.filter(
        Q(nom__icontains=q) | Q(dci__icontains=q)
    ).values('id', 'nom', 'dci', 'forme', 'dosage', 'categorie')[:30]
    return JsonResponse({'results': list(meds)})



def api_suggestions_medicaments(request):
    from django.http import JsonResponse
    from .models import Medicament
    from django.db.models import Q
    import json, os
    from django.conf import settings

    maladies_param = request.GET.get('maladies', '')
    if not maladies_param:
        return JsonResponse({'suggestions': []})

    maladies = maladies_param.split('|')

    # Charger le mapping
    mapping_path = os.path.join(settings.STATIC_ROOT, 'data', 'maladie_medicaments.json')
    if not os.path.exists(mapping_path):
        mapping_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'maladie_medicaments.json')

    try:
        with open(mapping_path, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
    except:
        return JsonResponse({'suggestions': []})

    suggestions = []
    seen_dci = set()

    for maladie in maladies:
        maladie = maladie.strip()
        rule = mapping.get(maladie)
        if not rule:
            continue

        for med_rule in rule.get('medicaments', []):
            dci = med_rule['dci']
            if dci in seen_dci:
                continue
            seen_dci.add(dci)

            # Chercher dans la base par DCI
            dci_search = dci.replace(' // ', '%').replace("'", '')
            db_meds = Medicament.objects.filter(
                dci__icontains=dci_search.split('%')[0]
            ).values('id', 'nom', 'dci', 'forme', 'dosage')[:5]

            if db_meds:
                suggestions.append({
                    'dci': dci,
                    'raison': med_rule['raison'],
                    'categorie': med_rule['categorie'],
                    'maladie': maladie,
                    'medicaments': list(db_meds)
                })

    return JsonResponse({'suggestions': suggestions})

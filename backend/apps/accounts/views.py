from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, MedecinProfile
from .services.medecin import creer_medecin, desactiver_medecin, reactiver_medecin, changer_statut_medecin


def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        return redirect('medecin_dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user and user.est_actif:
            login(request, user)
            if user.role == 'admin':
                return redirect('admin_dashboard')
            return redirect('medecin_dashboard')
        return render(request, 'auth/login.html', {'error': 'Email ou mot de passe incorrect'})

    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('medecin_dashboard')
    medecins = MedecinProfile.objects.select_related('user').all()
    from apps.patients.models import Patient
    patients = Patient.objects.all()
    return render(request, 'admin/dashboard.html', {
        'medecins': medecins,
        'patients': patients,
        'all_medecins': medecins,
    })


@login_required
def ajouter_medecin(request):
    if request.user.role != 'admin':
        return redirect('medecin_dashboard')

    if request.method == 'POST':
        try:
            medecin = creer_medecin(
                email=request.POST.get('email'),
                password=request.POST.get('password'),
                nom=request.POST.get('nom'),
                prenom=request.POST.get('prenom'),
                specialite=request.POST.get('specialite'),
                cree_par=request.user
            )
            messages.success(request, f'Dr. {medecin.prenom} {medecin.nom} créé avec succès')
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f'Erreur : {str(e)}')

    return render(request, 'admin/ajouter_medecin.html')


@login_required
def desactiver_medecin_view(request, medecin_id):
    if request.user.role != 'admin':
        return redirect('medecin_dashboard')
    medecin = get_object_or_404(MedecinProfile, id=medecin_id)
    desactiver_medecin(medecin)
    messages.success(request, f'Dr. {medecin.prenom} {medecin.nom} désactivé')
    return redirect('admin_dashboard')




@login_required
def reactiver_medecin_view(request, medecin_id):
    from apps.accounts.models import MedecinProfile
    from django.shortcuts import get_object_or_404
    if request.user.role != 'admin':
        return redirect('medecin_dashboard')
    medecin = get_object_or_404(MedecinProfile, id=medecin_id)
    reactiver_medecin(medecin)
    messages.success(request, f'Dr. {medecin.prenom} {medecin.nom} a été réactivé.')
    return redirect('admin_dashboard')
@login_required
def medecin_dashboard(request):
    if request.user.role != 'medecin':
        return redirect('admin_dashboard')
    medecin = get_object_or_404(MedecinProfile, user=request.user)
    from apps.consultations.models import Consultation
    recent_consultations = Consultation.objects.filter(
        medecin=medecin
    ).select_related('patient').order_by('-demandee_le')[:5]
    total = Consultation.objects.filter(medecin=medecin).count()
    cloturees = Consultation.objects.filter(medecin=medecin, statut='cloturee').count()
    en_attente = Consultation.objects.filter(statut='en_attente').count() if medecin.statut != 'indisponible' else 0
    return render(request, 'medecin/dashboard.html', {
        'medecin': medecin,
        'recent_consultations': recent_consultations,
        'total_consultations': total,
        'consultations_cloturees': cloturees,
        'consultations_en_attente': en_attente,
    })


@login_required
def changer_statut_view(request):
    if request.user.role != 'medecin':
        return redirect('admin_dashboard')
    if request.method == 'POST':
        nouveau_statut = request.POST.get('statut')
        medecin = get_object_or_404(MedecinProfile, user=request.user)
        changer_statut_medecin(medecin, nouveau_statut)
        messages.success(request, f'Statut mis à jour : {nouveau_statut}')
    return redirect('medecin_dashboard')


@login_required
def changer_medecin_traitant(request):
    if request.user.role != 'admin':
        return redirect('medecin_dashboard')
    if request.method == 'POST':
        from apps.patients.models import Patient, PatientMedecinTraitant
        patient_id = request.POST.get('patient_id')
        medecin_id = request.POST.get('medecin_id')
        patient = get_object_or_404(Patient, id=patient_id)
        # Fermer l'ancienne relation
        PatientMedecinTraitant.objects.filter(
            patient=patient, date_fin__isnull=True
        ).update(date_fin=timezone.now())
        # Créer la nouvelle relation si un médecin est sélectionné
        if medecin_id:
            medecin = get_object_or_404(MedecinProfile, id=medecin_id)
            PatientMedecinTraitant.objects.create(
                patient=patient, medecin=medecin
            )
        messages.success(request, 'Médecin traitant mis à jour')
    return redirect('admin_dashboard')


@login_required
def reset_password_medecin(request):
    if request.user.role != 'admin':
        return redirect('medecin_dashboard')
    if request.method == 'POST':
        medecin_id = request.POST.get('medecin_id')
        new_password = request.POST.get('new_password')
        if not new_password or len(new_password) < 6:
            messages.error(request, 'Le mot de passe doit contenir au moins 6 caractères')
            return redirect('admin_dashboard')
        medecin = get_object_or_404(MedecinProfile, id=medecin_id)
        medecin.user.set_password(new_password)
        medecin.user.save()
        messages.success(request, f'Mot de passe de Dr. {medecin.prenom} {medecin.nom} réinitialisé')
    return redirect('admin_dashboard')

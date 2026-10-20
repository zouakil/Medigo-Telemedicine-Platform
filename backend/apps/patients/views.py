from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Patient
from .services.patient import creer_patient


@login_required
def ajouter_patient(request):
    if request.user.role != 'admin':
        return redirect('medecin_dashboard')

    if request.method == 'POST':
        try:
            patient = creer_patient(
                nom=request.POST.get('nom'),
                prenom=request.POST.get('prenom'),
                cin=request.POST.get('cin'),
                telephone=request.POST.get('telephone'),
                date_naissance=request.POST.get('date_naissance'),
                sexe=request.POST.get('sexe') or None,
                ville=request.POST.get('ville') or None
            )
            messages.success(request, f'Patient {patient.prenom} {patient.nom} créé. Code : {patient.code_unique}')
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f'Erreur : {str(e)}')

    return render(request, 'admin/ajouter_patient.html')



@login_required
def toggle_patient_actif_view(request, patient_id):
    if request.user.role != 'admin':
        return redirect('medecin_dashboard')
    from django.shortcuts import get_object_or_404
    from .services.patient import toggle_patient_actif
    patient = get_object_or_404(Patient, id=patient_id)
    toggle_patient_actif(patient)
    statut = 'activé' if patient.est_actif else 'désactivé'
    messages.success(request, f'Patient {patient.prenom} {patient.nom} {statut}.')
    return redirect('admin_dashboard')

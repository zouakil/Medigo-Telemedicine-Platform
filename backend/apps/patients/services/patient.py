from django.db import transaction
from django.utils import timezone
from apps.patients.models import Patient, PatientMedecinTraitant


def creer_patient(nom, prenom, cin, telephone, date_naissance, sexe=None, ville=None):
    with transaction.atomic():
        patient = Patient.objects.create(
            nom=nom,
            prenom=prenom,
            cin=cin,
            telephone=telephone,
            date_naissance=date_naissance,
            sexe=sexe,
            ville=ville
        )
    return patient


def assigner_medecin_traitant(patient, medecin):
    with transaction.atomic():
        # Close current active treating doctor if exists
        PatientMedecinTraitant.objects.filter(
            patient=patient,
            date_fin__isnull=True
        ).update(date_fin=timezone.now())

        # Assign new treating doctor
        relation = PatientMedecinTraitant.objects.create(
            patient=patient,
            medecin=medecin
        )
    return relation


def get_medecin_traitant(patient):
    relation = PatientMedecinTraitant.objects.filter(
        patient=patient,
        date_fin__isnull=True
    ).select_related('medecin').first()
    return relation.medecin if relation else None




def toggle_patient_actif(patient):
    patient.est_actif = not patient.est_actif
    patient.save()
    return patient

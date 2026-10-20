from django.utils import timezone
from django.db import transaction


def desactiver_medecin(medecin_profile):
    with transaction.atomic():
        # 1. Deactivate the user account
        user = medecin_profile.user
        user.est_actif = False
        user.is_active = False
        user.save()

        # 2. Close all active treating doctor relationships
        medecin_profile.patients_traitants.filter(
            date_fin__isnull=True
        ).update(date_fin=timezone.now())

        # 3. Set doctor as unavailable
        medecin_profile.statut = 'indisponible'
        medecin_profile.save()

    return medecin_profile


def changer_statut_medecin(medecin_profile, nouveau_statut):
    statuts_valides = ['disponible', 'indisponible', 'occupe']
    if nouveau_statut not in statuts_valides:
        raise ValueError(f"Statut invalide : {nouveau_statut}")

    medecin_profile.statut = nouveau_statut
    medecin_profile.save()
    return medecin_profile


def creer_medecin(email, password, nom, prenom, specialite, cree_par):
    from apps.accounts.models import User, MedecinProfile

    with transaction.atomic():
        user = User.objects.create_user(
            email=email,
            password=password,
            role='medecin'
        )

        medecin = MedecinProfile.objects.create(
            user=user,
            nom=nom,
            prenom=prenom,
            specialite=specialite,
            cree_par=cree_par,
            statut='indisponible'
        )

    return medecin


def reactiver_medecin(medecin_profile):
    with transaction.atomic():
        user = medecin_profile.user
        user.est_actif = True
        user.is_active = True
        user.save()
        medecin_profile.statut = 'indisponible'
        medecin_profile.save()
    return medecin_profile

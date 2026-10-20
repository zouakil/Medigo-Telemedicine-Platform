import uuid
from django.db import models
from apps.accounts.models import MedecinProfile
from apps.patients.models import Patient


class Consultation(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('acceptee', 'Acceptée'),
        ('en_cours', 'En cours'),
        ('cloturee', 'Clôturée'),
        ('expiree', 'Expirée'),
    ]
    ENDED_BY_CHOICES = [
        ('medecin', 'Médecin'),
        ('systeme', 'Système'),
        ('timeout', 'Timeout'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name='consultations')
    medecin = models.ForeignKey(MedecinProfile, on_delete=models.PROTECT, related_name='consultations', null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    room_name = models.CharField(max_length=100, unique=True, null=True, blank=True)
    patient_joined_at = models.DateTimeField(null=True, blank=True)
    medecin_joined_at = models.DateTimeField(null=True, blank=True)
    ended_by = models.CharField(max_length=10, choices=ENDED_BY_CHOICES, null=True, blank=True)
    diagnostic = models.TextField(blank=True)
    notes_medecin = models.TextField(blank=True)
    demandee_le = models.DateTimeField(auto_now_add=True)
    acceptee_le = models.DateTimeField(null=True, blank=True)
    demarree_le = models.DateTimeField(null=True, blank=True)
    cloturee_le = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'consultation'
        indexes = [
            models.Index(fields=['patient']),
            models.Index(fields=['medecin']),
            models.Index(fields=['statut']),
        ]

    def __str__(self):
        return f"Consultation {self.patient} - {self.statut}"

    def est_premiere_consultation(self):
        return Consultation.objects.filter(
            patient=self.patient,
            statut='cloturee'
        ).count() == 0


class ConsultationSymptome(models.Model):
    INTENSITE_CHOICES = [
        (0, 'Aucune'),
        (1, 'Très légère'),
        (2, 'Légère'),
        (3, 'Modérée'),
        (4, 'Forte'),
        (5, 'Très forte'),
    ]
    EVOLUTION_CHOICES = [
        ('stable', 'Stable'),
        ('aggravation', 'Aggravation'),
        ('amelioration', 'Amélioration'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='symptomes')
    nom_symptome = models.CharField(max_length=200)
    intensite = models.IntegerField(choices=INTENSITE_CHOICES, default=0)
    evolution = models.CharField(max_length=20, choices=EVOLUTION_CHOICES, default='stable')
    ajoute_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'consultation_symptome'

    def __str__(self):
        return f"{self.nom_symptome} — {self.consultation}"


class PatientMaladie(models.Model):
    STATUT_CHOICES = [
        ('en_traitement', 'En traitement'),
        ('traite', 'Traité'),
        ('en_surveillance', 'En surveillance'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, on_delete=models.PROTECT, related_name='maladies')
    nom_maladie = models.CharField(max_length=200)
    est_chronique = models.BooleanField(default=False)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_traitement')
    notes = models.TextField(blank=True)
    diagnostiquee_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'patient_maladie'
        indexes = [
            models.Index(fields=['consultation']),
        ]

    def __str__(self):
        return f"{self.nom_maladie} - {self.statut}"


class MesureAnthropo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, on_delete=models.PROTECT, related_name='mesures_anthropo')
    taille_cm = models.FloatField(null=True, blank=True)
    poids_kg = models.FloatField(null=True, blank=True)
    tension_sys = models.IntegerField(null=True, blank=True, verbose_name='Pression systolique')
    tension_dia = models.IntegerField(null=True, blank=True, verbose_name='Pression diastolique')
    glycemie = models.FloatField(null=True, blank=True, verbose_name='Glycémie g/L')
    mesure_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mesure_anthropometrique'

    def __str__(self):
        return f"Taille: {self.taille_cm}cm Poids: {self.poids_kg}kg"


class PatientAllergie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='allergies')
    nom_allergie = models.CharField(max_length=200)
    ajoute_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'patient_allergie'

    def __str__(self):
        return self.nom_allergie


class InfoClinique(models.Model):
    TABAC_CHOICES = [
        ('non_fumeur', 'Non fumeur'),
        ('fumeur', 'Fumeur'),
        ('ancien_fumeur', 'Ancien fumeur'),
    ]
    ALCOOL_CHOICES = [
        ('jamais', 'Jamais'),
        ('occasionnel', 'Occasionnel'),
        ('regulier', 'Régulier'),
    ]
    ACTIVITE_CHOICES = [
        ('sedentaire', 'Sédentaire'),
        ('peu_actif', 'Peu actif'),
        ('actif', 'Actif'),
        ('tres_actif', 'Très actif'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, related_name='info_clinique')
    tabac = models.CharField(max_length=20, choices=TABAC_CHOICES, default='non_fumeur')
    alcool = models.CharField(max_length=20, choices=ALCOOL_CHOICES, default='jamais')
    activite_physique = models.CharField(max_length=20, choices=ACTIVITE_CHOICES, default='sedentaire')
    enceinte = models.BooleanField(null=True, blank=True)
    maladies_chroniques = models.BooleanField(default=False)
    sauvegarde_le = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'info_clinique'

    def __str__(self):
        return f"Info clinique — {self.consultation}"

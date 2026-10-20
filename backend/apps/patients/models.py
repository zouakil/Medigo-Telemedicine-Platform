import uuid
import secrets
import string
from django.db import models
from apps.accounts.models import MedecinProfile


def generate_code_unique():
    while True:
        code = ''.join(secrets.choice(string.digits) for _ in range(6))
        if not Patient.objects.filter(code_unique=code).exists():
            return code


SEXE_CHOICES = [('M', 'Masculin'), ('F', 'Féminin')]

GROUPE_SANGUIN_CHOICES = [
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
    ('O+', 'O+'), ('O-', 'O-'),
]


class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    cin = models.CharField(max_length=20, unique=True)
    telephone = models.CharField(max_length=20)
    ville = models.CharField(max_length=100, null=True, blank=True)
    date_naissance = models.DateField()
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES, null=True, blank=True)
    groupe_sanguin = models.CharField(max_length=5, choices=GROUPE_SANGUIN_CHOICES, null=True, blank=True)
    allergies = models.TextField(null=True, blank=True)
    code_unique = models.CharField(max_length=6, unique=True, editable=False)
    est_actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'patient'
        indexes = [
            models.Index(fields=['code_unique']),
            models.Index(fields=['cin']),
        ]

    def save(self, *args, **kwargs):
        if not self.code_unique:
            self.code_unique = generate_code_unique()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    def get_medecin_traitant(self):
        traitant = self.medecins_traitants.filter(
            date_fin__isnull=True
        ).first()
        return traitant.medecin if traitant else None

    @property
    def age(self):
        from datetime import date
        today = date.today()
        born = self.date_naissance
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


class PatientMedecinTraitant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medecins_traitants')
    medecin = models.ForeignKey(MedecinProfile, on_delete=models.RESTRICT, related_name='patients_traitants')
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'patient_medecin_traitant'
        indexes = [
            models.Index(fields=['patient', 'date_fin']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(date_fin__isnull=True) | models.Q(date_fin__gt=models.F('date_debut')),
                name='chk_dates_coherentes'
            )
        ]

    def __str__(self):
        return f"{self.patient} → Dr. {self.medecin}"

import uuid
from django.db import models
from apps.consultations.models import Consultation


class Medicament(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=200)
    dci = models.CharField(max_length=500, blank=True)
    forme = models.CharField(max_length=200, blank=True)
    dosage = models.CharField(max_length=100, blank=True)
    categorie = models.CharField(max_length=500, blank=True)

    class Meta:
        db_table = 'medicament'
        ordering = ['nom']
        indexes = [
            models.Index(fields=['nom']),
            models.Index(fields=['dci']),
            models.Index(fields=['categorie']),
        ]

    def __str__(self):
        parts = [self.nom]
        if self.dosage:
            parts.append(self.dosage)
        if self.forme:
            parts.append(self.forme)
        return ' — '.join(parts)


class Ordonnance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.OneToOneField(Consultation, on_delete=models.PROTECT, related_name='ordonnance')
    contenu = models.TextField()
    storage_key = models.CharField(max_length=500, blank=True)
    qr_code_key = models.CharField(max_length=500, blank=True)
    creee_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ordonnance'

    def __str__(self):
        return f"Ordonnance consultation {self.consultation_id}"


class OrdonnanceLigne(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ordonnance = models.ForeignKey(Ordonnance, on_delete=models.CASCADE, related_name='lignes')
    medicament = models.ForeignKey(Medicament, on_delete=models.PROTECT, related_name='ordonnance_lignes', null=True, blank=True)
    nom_medicament = models.CharField(max_length=300)
    posologie = models.CharField(max_length=300, blank=True)
    duree = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'ordonnance_ligne'

    def __str__(self):
        return f"{self.nom_medicament} — {self.posologie}"

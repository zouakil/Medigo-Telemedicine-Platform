import uuid
from django.db import models
from apps.consultations.models import Consultation


class Message(models.Model):
    EXPEDITEUR_CHOICES = [
        ('medecin', 'Médecin'),
        ('patient', 'Patient'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, on_delete=models.PROTECT, related_name='messages')
    expediteur = models.CharField(max_length=10, choices=EXPEDITEUR_CHOICES)
    contenu = models.TextField()
    est_alerte_urgente = models.BooleanField(default=False)
    envoye_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'message'
        indexes = [
            models.Index(fields=['consultation']),
        ]

    def __str__(self):
        return f"{self.expediteur} : {self.contenu[:50]}"


class ImageMedicale(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, on_delete=models.PROTECT, related_name='images')
    storage_key = models.CharField(max_length=500)
    storage_provider = models.CharField(max_length=50, default='local')
    nom_original = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, blank=True)
    file_size = models.IntegerField(null=True, blank=True)
    envoye_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'image_medicale'
        indexes = [
            models.Index(fields=['consultation']),
        ]

    def __str__(self):
        return f"{self.nom_original}"

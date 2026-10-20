import uuid
from django.db import models
from apps.consultations.models import Consultation


class SigneVital(models.Model):
    SOURCE_CHOICES = [
        ('max30102', 'MAX30102'),
        ('mlx90614', 'MLX90614'),
        ('combined', 'Combined'),
    ]
    QUALITE_CHOICES = [
        ('bon', 'Bon'),
        ('bruite', 'Bruité'),
        ('erreur', 'Erreur'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consultation = models.ForeignKey(Consultation, on_delete=models.PROTECT, related_name='signes_vitaux')
    spo2 = models.FloatField(null=True, blank=True)
    frequence_cardiaque = models.FloatField(null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='combined')
    qualite_lecture = models.CharField(max_length=10, choices=QUALITE_CHOICES, default='bon')
    enregistre_par_medecin = models.BooleanField(default=False)
    mesure_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'signe_vital'
        indexes = [
            models.Index(fields=['consultation', 'mesure_le']),
        ]

    def __str__(self):
        return f"SpO2:{self.spo2} FC:{self.frequence_cardiaque} T:{self.temperature}"

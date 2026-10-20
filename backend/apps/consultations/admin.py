from django.contrib import admin
from .models import Consultation, PatientMaladie, MesureAnthropo


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ['patient', 'medecin', 'statut', 'demandee_le', 'cloturee_le']
    list_filter = ['statut']
    search_fields = ['patient__nom', 'patient__prenom']
    ordering = ['-demandee_le']
    readonly_fields = ['demandee_le']


@admin.register(PatientMaladie)
class PatientMaladieAdmin(admin.ModelAdmin):
    list_display = ['nom_maladie', 'est_chronique', 'statut', 'consultation']
    list_filter = ['est_chronique', 'statut']
    search_fields = ['nom_maladie']


@admin.register(MesureAnthropo)
class MesureAnthropoAdmin(admin.ModelAdmin):
    list_display = ['consultation', 'taille_cm', 'poids_kg', 'mesure_le']

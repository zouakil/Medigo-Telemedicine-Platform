from django.contrib import admin
from .models import Patient, PatientMedecinTraitant


class MedecinTraitantInline(admin.TabularInline):
    model = PatientMedecinTraitant
    extra = 1
    fields = ['medecin', 'date_debut', 'date_fin']
    readonly_fields = ['date_debut']


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    inlines = [MedecinTraitantInline]
    list_display = ['nom', 'prenom', 'sexe', 'cin', 'telephone', 'code_unique', 'created_at']
    search_fields = ['nom', 'prenom', 'cin', 'code_unique']
    list_filter = ['sexe']
    readonly_fields = ['code_unique', 'created_at']
    ordering = ['-created_at']


@admin.register(PatientMedecinTraitant)
class PatientMedecinTraitantAdmin(admin.ModelAdmin):
    list_display = ['patient', 'medecin', 'date_debut', 'date_fin', 'est_actif']
    list_filter = ['date_fin', 'medecin']
    search_fields = ['patient__nom', 'patient__prenom', 'medecin__nom', 'medecin__prenom']
    list_editable = ['medecin']
    raw_id_fields = ['patient', 'medecin']

    def est_actif(self, obj):
        return obj.date_fin is None
    est_actif.boolean = True
    est_actif.short_description = 'Actif'

    def save_model(self, request, obj, form, change):
        if change and 'medecin' in form.changed_data:
            from django.utils import timezone
            PatientMedecinTraitant.objects.filter(
                patient=obj.patient,
                date_fin__isnull=True
            ).exclude(id=obj.id).update(date_fin=timezone.now())
        super().save_model(request, obj, form, change)

from django.contrib import admin
from .models import SigneVital


@admin.register(SigneVital)
class SigneVitalAdmin(admin.ModelAdmin):
    list_display = ['consultation', 'spo2', 'frequence_cardiaque', 'temperature', 'source', 'qualite_lecture', 'mesure_le']
    list_filter = ['source', 'qualite_lecture']
    ordering = ['-mesure_le']

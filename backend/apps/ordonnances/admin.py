from django.contrib import admin
from .models import Ordonnance


@admin.register(Ordonnance)
class OrdonnanceAdmin(admin.ModelAdmin):
    list_display = ['consultation', 'creee_le']
    ordering = ['-creee_le']

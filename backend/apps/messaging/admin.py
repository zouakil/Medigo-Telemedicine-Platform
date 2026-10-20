from django.contrib import admin
from .models import Message, ImageMedicale


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['consultation', 'expediteur', 'contenu', 'est_alerte_urgente', 'envoye_le']
    list_filter = ['expediteur', 'est_alerte_urgente']


@admin.register(ImageMedicale)
class ImageMedicaleAdmin(admin.ModelAdmin):
    list_display = ['consultation', 'nom_original', 'file_type', 'file_size', 'envoye_le']

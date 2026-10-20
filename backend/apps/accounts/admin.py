from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, MedecinProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'role', 'est_actif', 'created_at']
    list_filter = ['role', 'est_actif']
    search_fields = ['email']
    ordering = ['-created_at']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations', {'fields': ('role', 'est_actif')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )
    filter_horizontal = ()


@admin.register(MedecinProfile)
class MedecinProfileAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prenom', 'specialite', 'statut', 'user']
    list_filter = ['statut', 'specialite']
    search_fields = ['nom', 'prenom']

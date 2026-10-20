from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/changer-medecin-traitant/', views.changer_medecin_traitant, name='changer_medecin_traitant'),
    path('admin/reset-password-medecin/', views.reset_password_medecin, name='reset_password_medecin'),
    path('admin/medecin/ajouter/', views.ajouter_medecin, name='ajouter_medecin'),
    path('admin/medecin/<uuid:medecin_id>/desactiver/', views.desactiver_medecin_view, name='desactiver_medecin'),
    path('admin/medecin/<uuid:medecin_id>/reactiver/', views.reactiver_medecin_view, name='reactiver_medecin'),
    path('medecin/dashboard/', views.medecin_dashboard, name='medecin_dashboard'),
    path('medecin/statut/', views.changer_statut_view, name='changer_statut'),
]

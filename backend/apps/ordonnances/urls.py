from django.urls import path
from . import views

urlpatterns = [
    path('consultation/<uuid:consultation_id>/ordonnance/', views.creer_ordonnance, name='creer_ordonnance'),
    path('ordonnance/<uuid:ordonnance_id>/', views.voir_ordonnance_medecin, name='voir_ordonnance'),
    path('patient/ordonnance/<uuid:ordonnance_id>/', views.voir_ordonnance_patient, name='patient_ordonnance'),
    path('patient/ordonnances/', views.liste_ordonnances_patient, name='patient_ordonnances'),
    path('ordonnance/<uuid:ordonnance_id>/pdf/', views.telecharger_pdf, name='telecharger_pdf'),
    path('api/medicaments/', views.api_recherche_medicaments, name='api_recherche_medicaments'),
    path('api/suggestions-medicaments/', views.api_suggestions_medicaments, name='api_suggestions_medicaments'),
]

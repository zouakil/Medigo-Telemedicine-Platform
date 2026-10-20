from django.urls import path
from . import views

urlpatterns = [
    path('ajouter/', views.ajouter_patient, name='ajouter_patient'),
    path('admin/patient/<uuid:patient_id>/toggle-actif/', views.toggle_patient_actif_view, name='toggle_patient_actif'),
]

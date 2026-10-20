from django.urls import path
from . import views

urlpatterns = [
    path('data/', views.recevoir_donnees_capteurs, name='sensor_data'),
    path('active-consultation/', views.get_active_consultation, name='active_consultation'),
    path('controler/', views.controler_capteurs, name='controler_capteurs'),
    path('capteurs-actifs/', views.get_capteurs_actifs_api, name='capteurs_actifs'),
    path('enregistrer-mesures/', views.enregistrer_mesures, name='enregistrer_mesures'),
]

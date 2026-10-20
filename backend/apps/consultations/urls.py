from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # --- Vues Patient ---
    path('patient/login/', views.patient_login, name='patient_login'),
    path('patient/menu/', views.patient_menu, name='patient_menu'),
    path('patient/', views.patient_choisir_langue, name='patient_choisir_langue'),
    path('patient/lang/<str:lang>/', views.patient_set_lang, name='patient_set_lang'),
    path('patient/change-lang/<str:lang>/', views.patient_change_lang, name='patient_change_lang'),
    path('patient/consultation/', views.patient_consultation, name='patient_consultation'),
    path('patient/logout/', views.patient_logout, name='patient_logout'),
    path('patient/live/<uuid:consultation_id>/', views.patient_live, name='patient_live'),
    path('patient/historique/', views.patient_historique, name='patient_historique'),
    path('patient/signes-vitaux/', views.patient_signes_vitaux, name='patient_signes_vitaux'),
    path('patient/au-secours/', views.au_secours, name='au_secours'),
    path('patient/annuler-consultation/', views.annuler_consultation, name='annuler_consultation'),
    path('patient/attente-ordonnance/<uuid:consultation_id>/', views.patient_attente_ordonnance, name='patient_attente_ordonnance'),
    path('patient/consultation-terminee/', views.patient_consultation_terminee, name='patient_consultation_terminee'),

    # --- Vues Médecin ---
    path('medecin/consultations/', views.medecin_consultations, name='medecin_consultations'),
    path('medecin/consultations/api/', views.api_consultations_en_attente, name='api_consultations'),
    path('medecin/mes-patients/', views.mes_patients, name='mes_patients'),
    path('medecin/patients/<uuid:patient_id>/', views.fiche_patient, name='fiche_patient'),

    # --- Vues Consultation ---
    path('consultations/<uuid:consultation_id>/debriefing/', views.debriefing, name='debriefing'),
    path('consultations/<uuid:consultation_id>/demarrer/', views.demarrer_consultation, name='demarrer_consultation'),
    path('consultations/<uuid:consultation_id>/cloturer/', views.cloturer_consultation, name='cloturer_consultation'),
    path('consultations/<uuid:consultation_id>/voir/', views.voir_consultation, name='voir_consultation'),

    # --- API existantes ---
    path('api/consultation/symptomes/', api_views.sauvegarder_symptomes, name='sauvegarder_symptomes'),
    path('api/consultation/mesures/', api_views.sauvegarder_mesures, name='sauvegarder_mesures'),
    path('api/consultation/infos-patient/', api_views.sauvegarder_infos_patient, name='sauvegarder_infos_patient'),
    path('api/consultation/maladies/', api_views.sauvegarder_maladies, name='sauvegarder_maladies'),
    path('api/consultation/allergies/', api_views.sauvegarder_allergies, name='sauvegarder_allergies'),
    path('api/consultation/info-clinique/', api_views.sauvegarder_info_clinique, name='sauvegarder_info_clinique'),
    path('api/consultation/check-active/', api_views.check_consultation_active, name='check_consultation_active'),
    path('api/consultation/notifier-fin/', views.notifier_fin_consultation, name='notifier_fin_consultation'),

    # --- NOUVELLES API MEDIGO IA ---
    path('api/medigo/symptomes/', api_views.api_medigo_symptomes, name='api_medigo_symptomes'),
    path('api/medigo/maladies/', api_views.api_medigo_maladies, name='api_medigo_maladies'),
    path('api/consultation/<uuid:consultation_id>/ia-live/', api_views.api_ia_live, name='api_ia_live'),
    path('api/consultation/<uuid:consultation_id>/patient-summary/', api_views.api_patient_summary, name='api_patient_summary'),
    path('api/consultation/normalize-symptome/', api_views.api_normalize_symptome, name='api_normalize_symptome'),
]

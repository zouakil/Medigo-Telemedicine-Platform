"""
Middleware MEDIGO - Protection des routes patient
- Si pas de langue choisie → redirection vers /patient/ (choix langue)
- Si pas connecté → redirection vers /patient/login/
"""
from django.shortcuts import redirect
from django.urls import resolve, Resolver404


# Routes patient qui n'exigent PAS de connexion (mais peuvent exiger une langue)
PATIENT_PUBLIC_URLS = {
    'patient_choisir_langue',
    'patient_set_lang',
    'patient_change_lang',
    'patient_login',
    'patient_ordonnance',  # Accessible via QR code (verification par code patient)
    'telecharger_pdf',  # Téléchargement PDF via QR
}

# Routes patient qui exigent connexion ET langue
PATIENT_PROTECTED_URLS = {
    'patient_menu',
    'patient_consultation',
    'patient_logout',
    'patient_live',
    'patient_historique',
    'patient_signes_vitaux',
    'patient_ordonnances',
    'patient_ordonnance',
    'patient_attente_ordonnance',
    'patient_consultation_terminee',
}


class PatientI18nMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Identifier la route
        try:
            url_name = resolve(request.path_info).url_name
        except Resolver404:
            return self.get_response(request)

        # Si c'est une route patient
        if url_name and (url_name in PATIENT_PUBLIC_URLS or url_name in PATIENT_PROTECTED_URLS):

            # Skip pour la page de choix de langue elle-même
            if url_name == 'patient_choisir_langue':
                return self.get_response(request)

            # Skip pour set_lang et change_lang (ils gèrent eux-mêmes)
            if url_name in ('patient_set_lang', 'patient_change_lang'):
                return self.get_response(request)

            # Pour les routes accessibles par QR code : définir langue par défaut
            QR_CODE_ROUTES = {'patient_ordonnance', 'telecharger_pdf'}
            if url_name in QR_CODE_ROUTES:
                if not request.session.get('patient_lang'):
                    request.session['patient_lang'] = 'fr'  # Default
                return self.get_response(request)

            # Vérifier qu'une langue est choisie
            if not request.session.get('patient_lang'):
                return redirect('patient_choisir_langue')

            # Pour les routes protégées, vérifier la connexion
            if url_name in PATIENT_PROTECTED_URLS:
                if not request.session.get('patient_id'):
                    return redirect('patient_login')

        return self.get_response(request)

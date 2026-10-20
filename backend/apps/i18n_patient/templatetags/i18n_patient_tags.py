from django import template
from apps.i18n_patient.translations import get_translation, is_rtl

register = template.Library()


@register.simple_tag(takes_context=True)
def t(context, key):
    """Tag template pour traduire: {% t "key" %}"""
    request = context.get('request')
    lang = 'fr'
    if request and hasattr(request, 'session'):
        lang = request.session.get('patient_lang', 'fr')
    return get_translation(key, lang)


@register.simple_tag(takes_context=True)
def get_lang(context):
    """Retourne la langue actuelle."""
    request = context.get('request')
    if request and hasattr(request, 'session'):
        return request.session.get('patient_lang', 'fr')
    return 'fr'


@register.simple_tag(takes_context=True)
def get_dir(context):
    """Retourne 'rtl' ou 'ltr' selon la langue."""
    request = context.get('request')
    lang = 'fr'
    if request and hasattr(request, 'session'):
        lang = request.session.get('patient_lang', 'fr')
    return 'rtl' if is_rtl(lang) else 'ltr'

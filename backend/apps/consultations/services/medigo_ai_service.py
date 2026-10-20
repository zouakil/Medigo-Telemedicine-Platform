"""
MEDIGO IA Service — Service d'inférence hybride (rule-based + XGBoost)
À placer dans: backend/apps/consultations/services/medigo_ai_service.py

Charge le modèle XGBoost une seule fois (singleton).
Fusionne le score rule-based (65%) et XGBoost (35%) pour chaque maladie.
Construit le patient_context depuis les modèles Django.
"""

import logging
import os
import sys
import threading
from datetime import date
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Chemin vers le dossier medigo_ai (à côté de backend/)
# ---------------------------------------------------------------------------
_AI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), 'medigo_ai')

if _AI_DIR not in sys.path:
    sys.path.insert(0, os.path.dirname(_AI_DIR))

from medigo_ai.medigo_kb_v2_complete import (
    MALADIES,
    MALADIE_TO_LABEL,
    SYMPTOMES_CANONIQUES,
    diagnostiquer,
    detecter_red_flags,
    mapper_symptome,
    normaliser_symptomes,
    orientation_triage,
    scorer_diagnostics,
    validate_knowledge_base,
)
from medigo_ai.medigo_features import vectoriser_patient

# ---------------------------------------------------------------------------
# 1) Chargement singleton du modèle XGBoost
# ---------------------------------------------------------------------------

_bundle = None
_bundle_lock = threading.Lock()


def load_ai_bundle() -> Dict[str, Any]:
    """Charge le modèle .joblib une seule fois (thread-safe)."""
    from django.conf import settings
    if not settings.ENABLE_XGBOOST:
        raise RuntimeError('XGBoost is disabled; using the rule-based engine')
    global _bundle
    if _bundle is not None:
        return _bundle

    with _bundle_lock:
        if _bundle is not None:
            return _bundle

        import joblib
        model_path = os.path.join(_AI_DIR, 'medigo_model_patient.joblib')
        logger.info("Chargement du modèle MEDIGO IA depuis %s ...", model_path)
        _bundle = joblib.load(model_path)
        logger.info(
            "Modèle chargé: version=%s, maladies=%d, features=%d",
            _bundle.get('version', '?'),
            len(_bundle.get('label_to_maladie', {})),
            len(_bundle.get('feature_names', [])),
        )
        return _bundle


# ---------------------------------------------------------------------------
# 2) Construction du patient_context depuis les modèles Django
# ---------------------------------------------------------------------------

def build_patient_context(consultation) -> Dict[str, Any]:
    """
    Construit le dictionnaire patient_context attendu par vectoriser_patient()
    à partir d'une instance de Consultation Django.
    """
    patient = consultation.patient

    # --- Âge ---
    age = 0
    if patient.date_naissance:
        today = date.today()
        age = today.year - patient.date_naissance.year
        if (today.month, today.day) < (patient.date_naissance.month, patient.date_naissance.day):
            age -= 1

    # --- Sexe ---
    sexe_raw = getattr(patient, 'sexe', '') or ''
    sexe = 'homme' if sexe_raw.upper() in ('M', 'HOMME', 'MASCULIN') else 'femme'

    # --- Symptômes ---
    from apps.consultations.models import ConsultationSymptome
    symptomes_qs = ConsultationSymptome.objects.filter(consultation=consultation)
    symptomes = []
    for s in symptomes_qs:
        symptomes.append({
            'nom': s.nom_symptome,
            'intensite': s.intensite or 0,
            'evolution': s.evolution or 'stable',
        })

    # --- Mesures anthropométriques ---
    from apps.consultations.models import MesureAnthropo
    mesure = MesureAnthropo.objects.filter(consultation=consultation).last()
    tension_sys = getattr(mesure, 'tension_sys', None) if mesure else None
    tension_dia = getattr(mesure, 'tension_dia', None) if mesure else None
    glycemie = getattr(mesure, 'glycemie', None) if mesure else None

    # --- Signes vitaux (capteurs désactivés — on utilise les mesures manuelles uniquement) ---
    spo2 = None
    bpm = None
    temperature = None

    # --- Info clinique ---
    from apps.consultations.models import InfoClinique
    try:
        info = InfoClinique.objects.get(consultation=consultation)
    except InfoClinique.DoesNotExist:
        info = None

    grossesse = False
    maladies_chroniques = ''
    if info:
        grossesse = bool(getattr(info, 'enceinte', False))
        mc_raw = getattr(info, 'maladies_chroniques', '')
        # maladies_chroniques peut être un BooleanField — convertir en string
        maladies_chroniques = str(mc_raw) if mc_raw and not isinstance(mc_raw, bool) else ''

    # --- Antécédents (depuis PatientMaladie + maladies_chroniques) ---
    from apps.consultations.models import PatientMaladie
    antecedents_qs = PatientMaladie.objects.filter(
        consultation__patient=patient,
        est_chronique=True
    ).values_list('nom_maladie', flat=True)
    antecedents_texte = ' '.join([str(x) for x in antecedents_qs] + [maladies_chroniques]).lower()

    antecedents = {
        'diabete': 'diab' in antecedents_texte,
        'hta': 'hta' in antecedents_texte or 'hypertension' in antecedents_texte,
        'cardiaque': 'cardia' in antecedents_texte or 'coronar' in antecedents_texte,
        'asthme': 'asthme' in antecedents_texte,
        'bpco': 'bpco' in antecedents_texte,
        'grossesse': grossesse,
    }

    # --- Allergies ---
    from apps.consultations.models import PatientAllergie
    allergies = list(
        PatientAllergie.objects.filter(
            consultation__patient=patient
        ).values_list('nom_allergie', flat=True).distinct()
    )

    return {
        'age': age,
        'sexe': sexe,
        'symptomes': symptomes,
        'temperature': temperature,
        'spo2': spo2,
        'bpm': bpm,
        'tension_systolique': tension_sys,
        'tension_diastolique': tension_dia,
        'glycemie': glycemie,
        'grossesse': grossesse,
        'antecedents': antecedents,
        'allergies': allergies,
    }


# ---------------------------------------------------------------------------
# 3) Prédiction XGBoost
# ---------------------------------------------------------------------------

def predict_xgboost(patient_context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Lance predict_proba() sur le modèle XGBoost.
    Retourne une liste triée de {maladie, score_xgboost}.
    """
    bundle = load_ai_bundle()
    model = bundle['model']
    label_to_maladie = bundle['label_to_maladie']
    num_symptom_features = bundle.get('num_symptom_features')

    # Vectoriser le patient
    x = vectoriser_patient(patient_context, expected_num_symptom_features=num_symptom_features)
    x = x.reshape(1, -1)

    # Prédiction
    probas = model.predict_proba(x)[0]

    results = []
    for label_idx, proba in enumerate(probas):
        maladie_nom = label_to_maladie.get(label_idx) or label_to_maladie.get(str(label_idx))
        if maladie_nom and proba > 0.001:
            results.append({
                'maladie': maladie_nom,
                'score_xgboost': round(float(proba), 6),
            })

    results.sort(key=lambda x: x['score_xgboost'], reverse=True)
    return results


# ---------------------------------------------------------------------------
# 4) Fusion hybride rule-based + XGBoost
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Prévalence Maroc — Source: IHME GBD, OMS, Min. Santé Maroc
# Maladies courantes boostées, rares pénalisées
# ---------------------------------------------------------------------------
PREVALENCE_MAROC = {
    # ══════════════════════════════════════════════════════════════
    # TRÈS COURANTES — 1ers motifs de consultation au Maroc (×1.5)
    # ══════════════════════════════════════════════════════════════
    'Grippe / Syndrome grippal': 1.6,
    'COVID-19': 1.5,
    'Rhinopharyngite': 1.6,
    'Angine': 1.5,
    'Pharyngite': 1.5,
    'Rhume': 1.6,

    # Respiratoire courant
    'Bronchite aiguë': 1.45,
    'Sinusite': 1.4,
    'Otite moyenne aiguë': 1.4,
    'Laryngite': 1.35,

    # Digestif courant
    'Gastro-entérite aiguë': 1.5,
    'Toxi-infection alimentaire collective': 1.4,
    'Gastrite': 1.35,
    'Reflux gastro-œsophagien': 1.3,
    'Syndrome du côlon irritable': 1.25,
    'Ulcère gastrique': 1.2,

    # Douleur / MSK courant
    'Lombalgie commune': 1.4,
    'Arthrose': 1.35,
    'Cervicalgie': 1.3,
    'Sciatique': 1.25,
    'Tendinite': 1.3,

    # Dermatologie courante
    'Eczéma de contact': 1.35,
    'Dermatite atopique': 1.3,
    'Gale': 1.35,
    'Mycose cutanée / Dermatophytose': 1.35,
    'Acné': 1.3,
    'Urticaire': 1.25,
    'Impétigo': 1.2,

    # Urinaire courant
    'Infection urinaire basse / Cystite': 1.4,
    'Pyélonéphrite': 1.15,

    # Pédiatrie / infectieux courant Maroc
    'Bronchiolite': 1.3,
    'Conjonctivite': 1.35,
    'Varicelle': 0.85,  # vaccinée
    'Rougeole': 0.7,  # vaccinée au Maroc
    'Scarlatine': 0.8,

    # Neurologie courante
    'Migraine': 1.4,
    'Céphalée de tension': 1.4,
    'Névralgie cervico-brachiale': 1.2,

    # ORL courant
    'Rhinite allergique': 1.35,

    # Gynéco courant
    'Vaginite / Vaginose': 1.3,
    'Infection génitale basse': 1.25,
    'Dysménorrhée primaire': 1.25,

    # ══════════════════════════════════════════════════════════════
    # MALADIES CHRONIQUES FRÉQUENTES au Maroc (×1.2-1.3)
    # HTA: 19.5% | Diabète: 10.7% de la population adulte
    # ══════════════════════════════════════════════════════════════
    'Hypertension artérielle': 1.3,
    'Diabète type 2': 1.3,
    'Diabète type 1': 1.1,
    'Asthme (crise)': 1.25,
    'BPCO (exacerbation)': 1.15,
    'Anémie ferriprive': 1.3,
    'Hypothyroïdie': 1.15,
    'Hyperthyroïdie': 1.1,
    'Goutte': 1.15,
    'Allergie alimentaire': 1.2,

    # ══════════════════════════════════════════════════════════════
    # STANDARD — pas de modification (×1.0 implicite)
    # Pneumonie, Appendicite, Cholécystite, etc.
    # ══════════════════════════════════════════════════════════════
    'Pneumonie communautaire': 1.1,
    'Appendicite': 1.05,
    'Cholécystite': 1.05,
    'Pancréatite aiguë': 1.0,
    'Diverticulite aiguë': 1.0,
    'Prostatite aiguë': 1.0,
    'Zona': 1.0,
    'Coqueluche': 1.0,

    # ══════════════════════════════════════════════════════════════
    # PEU COURANTES au Maroc (×0.7-0.85)
    # ══════════════════════════════════════════════════════════════
    'Brucellose': 0.7,
    'Fièvre typhoïde': 0.75,
    'Leishmaniose viscérale': 0.65,
    'Leishmaniose cutanée': 0.75,
    'Paludisme / Malaria': 0.7,
    'Leptospirose': 0.6,
    'Fièvre Q': 0.55,
    'Maladie de Crohn': 0.75,
    'Rectocolite hémorragique': 0.75,
    'Lupus érythémateux': 0.7,
    'Sclérodermie': 0.6,
    'Vascularite': 0.65,
    'Sarcoïdose': 0.6,
    'Mononucléose infectieuse': 0.8,
    'Tuberculose pulmonaire': 0.9,

    # ══════════════════════════════════════════════════════════════
    # RARES au Maroc (×0.4-0.6)
    # ══════════════════════════════════════════════════════════════
    'VIH primo-infection': 0.5,
    'Endocardite infectieuse': 0.5,
    'Myasthénie': 0.45,
    'Guillain-Barré': 0.45,
    'Phéochromocytome': 0.4,
    'Maladie de Behçet': 0.55,
    'Pemphigus': 0.4,
    'Purpura thrombopénique': 0.5,
    'Encéphalite': 0.55,
    'Convulsion fébrile': 0.7,
    'Myocardite': 0.5,
    'Péricardite aiguë': 0.6,
    'Embolie pulmonaire': 0.65,
}

WEIGHT_RULE_BASED = 0.70
WEIGHT_XGBOOST = 0.30


def merge_scores(
    rule_based_results: List[Dict[str, Any]],
    xgboost_results: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Fusionne les scores rule-based et XGBoost.
    score_final = 0.65 * rule_based + 0.35 * xgboost
    """
    # Indexer par nom de maladie
    rb_map = {r['maladie']: r for r in rule_based_results}
    xgb_map = {r['maladie']: r for r in xgboost_results}

    all_maladies = set(rb_map.keys()) | set(xgb_map.keys())
    merged = []

    for nom in all_maladies:
        rb = rb_map.get(nom, {})
        xgb = xgb_map.get(nom, {})

        score_rb = rb.get('score', 0.0)
        score_xgb = xgb.get('score_xgboost', 0.0)

        # Si le rule-based donne 0 (aucun symptôme correspondant),
        # XGBoost est probablement du bruit → forte pénalité
        if score_rb < 0.01 and score_xgb > 0:
            score_final = WEIGHT_XGBOOST * score_xgb * 0.15  # pénalité x0.15
        else:
            score_final = WEIGHT_RULE_BASED * score_rb + WEIGHT_XGBOOST * score_xgb

        # Appliquer la prévalence Maroc
        prevalence = PREVALENCE_MAROC.get(nom, 1.0)
        score_final = score_final * prevalence

        if score_final < 0.01:
            continue

        # Construire l'explication
        explication = {
            'raison_courte': _generer_raison_courte(rb, score_rb, score_xgb),
            'symptomes_correspondants': rb.get('symptomes_correspondants', []),
            'symptomes_importants_manquants': rb.get('symptomes_importants_manquants', []),
            'facteurs_patient': [],  # sera enrichi par le contexte patient
            'red_flags_associes': rb.get('red_flags_maladie', []),
        }

        merged.append({
            'maladie': nom,
            'score_final': round(score_final, 4),
            'score_rule_based': round(score_rb, 4),
            'score_xgboost': round(score_xgb, 4),
            'categorie': rb.get('categorie', xgb.get('categorie', '')),
            'urgence': rb.get('urgence', False),
            'explication': explication,
            'questions': rb.get('questions', []),
        })

    merged.sort(key=lambda x: (x['score_final'], x['urgence']), reverse=True)
    return merged


def _generer_raison_courte(rb_result: Dict, score_rb: float, score_xgb: float) -> str:
    """Génère une explication courte du diagnostic."""
    correspondants = rb_result.get('symptomes_correspondants', [])
    if not correspondants:
        return "Suggestion basée sur le modèle statistique."

    nb = len(correspondants)
    top_symptomes = ', '.join(correspondants[:3])
    extras = f" et {nb - 3} autre(s)" if nb > 3 else ""

    if score_rb > 0.5:
        return f"Tableau clinique évocateur avec {top_symptomes}{extras}."
    elif score_rb > 0.25:
        return f"Plusieurs symptômes compatibles : {top_symptomes}{extras}."
    else:
        return f"Quelques symptômes compatibles : {top_symptomes}{extras}."


# ---------------------------------------------------------------------------
# 5) Enrichir avec les facteurs patient
# ---------------------------------------------------------------------------

def _enrichir_facteurs_patient(
    merged: List[Dict[str, Any]],
    patient_context: Dict[str, Any],
) -> None:
    """Ajoute les facteurs patient dans l'explication de chaque diagnostic."""
    facteurs = []
    age = patient_context.get('age', 0)
    if age > 45:
        facteurs.append(f"Âge > 45 ans ({age} ans)")
    if age > 65:
        facteurs.append(f"Âge > 65 ans ({age} ans)")

    antecedents = patient_context.get('antecedents', {})
    if antecedents.get('diabete'):
        facteurs.append("Antécédent diabète")
    if antecedents.get('hta'):
        facteurs.append("Antécédent HTA")
    if antecedents.get('cardiaque'):
        facteurs.append("Antécédent cardiaque")
    if antecedents.get('asthme'):
        facteurs.append("Antécédent asthme")
    if antecedents.get('bpco'):
        facteurs.append("Antécédent BPCO")
    if antecedents.get('grossesse') or patient_context.get('grossesse'):
        facteurs.append("Grossesse")

    spo2 = patient_context.get('spo2')
    if spo2 and spo2 < 94:
        facteurs.append(f"SpO2 basse ({spo2}%)")

    bpm = patient_context.get('bpm')
    if bpm and bpm > 100:
        facteurs.append(f"BPM élevé ({bpm})")

    temp = patient_context.get('temperature')
    if temp and temp >= 38:
        facteurs.append(f"Fièvre ({temp}°C)")

    for entry in merged:
        entry['explication']['facteurs_patient'] = facteurs


# ---------------------------------------------------------------------------
# 6) Normalisation de symptôme libre (3 niveaux)
# ---------------------------------------------------------------------------

def normalize_symptom_input(texte: str) -> Dict[str, Any]:
    """
    Normalise un symptôme libre saisi par le médecin.
    Retourne le mapping avec le statut (confirme_auto / a_confirmer / non_reconnu).
    """
    from difflib import SequenceMatcher

    texte = texte.strip()
    if not texte:
        return {'statut_mapping': 'non_reconnu', 'symptome_original': texte}

    # Essai exact/synonyme
    mapped = mapper_symptome(texte, fuzzy=False)
    if mapped:
        return {
            'symptome_original': texte,
            'symptome_canonique': mapped,
            'source': 'manuel',
            'confiance_mapping': 1.0,
            'statut_mapping': 'canonique',
        }

    # Fuzzy matching avec scores
    from medigo_ai.medigo_kb_v2_complete import normaliser_texte, _NORMALIZED_SYMPTOMS, _NORMALIZED_SYNONYMS
    n = normaliser_texte(texte)

    # Calculer les scores pour tous les symptômes canoniques
    scores = []
    all_targets = {}

    for norm_key, canon in _NORMALIZED_SYMPTOMS.items():
        ratio = SequenceMatcher(None, n, norm_key).ratio()
        all_targets[canon] = max(all_targets.get(canon, 0), ratio)

    for norm_key, canon in _NORMALIZED_SYNONYMS.items():
        ratio = SequenceMatcher(None, n, norm_key).ratio()
        all_targets[canon] = max(all_targets.get(canon, 0), ratio)

    # Trier par score
    scores = sorted(all_targets.items(), key=lambda x: x[1], reverse=True)

    if not scores:
        return {
            'symptome_original': texte,
            'symptome_canonique': None,
            'source': 'manuel',
            'confiance_mapping': 0.0,
            'statut_mapping': 'non_reconnu',
        }

    best_name, best_score = scores[0]

    # CAS A — Correspondance fiable (>= 0.80)
    if best_score >= 0.80:
        return {
            'symptome_original': texte,
            'symptome_canonique': best_name,
            'source': 'manuel',
            'confiance_mapping': round(best_score, 4),
            'statut_mapping': 'confirme_auto',
        }

    # CAS B — Correspondance moyenne (0.60 - 0.79)
    if best_score >= 0.60:
        suggestions = [{'nom': name, 'score': round(sc, 4)} for name, sc in scores[:5] if sc >= 0.50]
        return {
            'symptome_original': texte,
            'symptome_canonique': None,
            'source': 'manuel',
            'confiance_mapping': round(best_score, 4),
            'statut_mapping': 'a_confirmer',
            'suggestions': suggestions,
        }

    # CAS C — Aucune correspondance (< 0.60)
    return {
        'symptome_original': texte,
        'symptome_canonique': None,
        'source': 'manuel',
        'confiance_mapping': round(best_score, 4),
        'statut_mapping': 'non_reconnu',
    }


# ---------------------------------------------------------------------------
# 7) Fonction principale — Prédiction live complète
# ---------------------------------------------------------------------------

def predict_live_consultation(consultation_id: int) -> Dict[str, Any]:
    """
    Point d'entrée principal pour l'IA live.
    Orchestre: patient_context → rule-based + XGBoost → fusion → retour.
    """
    from apps.consultations.models import Consultation

    try:
        consultation = Consultation.objects.select_related('patient').get(id=consultation_id)
    except Consultation.DoesNotExist:
        return {'error': 'Consultation introuvable', 'diagnostics': []}

    # 1. Construire le contexte patient
    patient_context = build_patient_context(consultation)

    # 2. Extraire les noms de symptômes pour le rule-based
    symptome_names = [s['nom'] for s in patient_context.get('symptomes', [])]

    if not symptome_names:
        return {
            'diagnostics': [],
            'red_flags': [],
            'orientation': {'niveau': 'orientation_standard', 'message': 'Aucun symptôme saisi.'},
            'questions_suivantes': [],
        }

    # 3. Construire les vitaux pour le rule-based
    vitaux = {}
    if patient_context.get('temperature'):
        vitaux['temperature'] = patient_context['temperature']
    if patient_context.get('spo2'):
        vitaux['spo2'] = patient_context['spo2']
    if patient_context.get('bpm'):
        vitaux['fc'] = patient_context['bpm']
    if patient_context.get('tension_systolique'):
        vitaux['tension_systolique'] = patient_context['tension_systolique']
    if patient_context.get('tension_diastolique'):
        vitaux['tension_diastolique'] = patient_context['tension_diastolique']

    # 4. Rule-based
    def _appliquer_prevalence(hypotheses):
        for h in hypotheses:
            h["score"] = h["score"] * PREVALENCE_MAROC.get(h["maladie"], 1.0)
        hypotheses.sort(key=lambda x: x["score"], reverse=True)
        return hypotheses

    rule_result = diagnostiquer(
        symptomes=symptome_names,
        vitaux=vitaux if vitaux else None,
        top_k=30,
        fuzzy=True,
    )

    rule_result["hypotheses"] = _appliquer_prevalence(rule_result["hypotheses"])

    # 5. XGBoost
    try:
        xgb_results = predict_xgboost(patient_context)
    except Exception as e:
        logger.warning("XGBoost prediction failed: %s — fallback rule-based only", e)
        xgb_results = []

    # 6. Fusion hybride
    if xgb_results:
        merged = merge_scores(rule_result['hypotheses'], xgb_results)
    else:
        merged = [{
            'maladie': h['maladie'],
            'score_final': h['score'],
            'score_rule_based': h['score'],
            'score_xgboost': 0.0,
            'categorie': h.get('categorie', ''),
            'urgence': h.get('urgence', False),
            'explication': {
                'raison_courte': f"Basé sur les symptômes correspondants.",
                'symptomes_correspondants': h.get('symptomes_correspondants', []),
                'symptomes_importants_manquants': h.get('symptomes_importants_manquants', []),
                'facteurs_patient': [],
                'red_flags_associes': h.get('red_flags_maladie', []),
            },
            'questions': h.get('questions', []),
        } for h in rule_result['hypotheses']]

    # 7. Enrichir avec les facteurs patient
    _enrichir_facteurs_patient(merged, patient_context)

    # 8. Résultat final
    return {
        'diagnostics': merged[:10],
        'red_flags': rule_result.get('red_flags', []),
        'orientation': rule_result.get('orientation', {}),
        'questions_suivantes': rule_result.get('questions_suivantes', []),
        'symptomes_reconnus': rule_result.get('symptomes_reconnus', []),
        'symptomes_inconnus': rule_result.get('symptomes_inconnus', []),
    }


# ---------------------------------------------------------------------------
# 8) Fonctions utilitaires pour les endpoints API
# ---------------------------------------------------------------------------

def get_symptomes_canoniques_grouped() -> Dict[str, List[str]]:
    """Retourne les symptômes canoniques groupés par catégorie."""
    categories = {}
    # Grouper par les catégories définies dans les commentaires de SYMPTOMES_CANONIQUES
    groups = {
        'Généraux': (0, 14),
        'Respiratoires': (15, 29),
        'Digestifs': (30, 44),
        'Urinaires': (45, 54),
        'Cardiovasculaires': (55, 64),
        'Neurologiques': (65, 79),
        'Musculo-squelettiques': (80, 89),
        'Dermatologiques': (90, 99),
        'ORL': (100, 109),
        'Gynécologiques': (110, 114),
        'Endocriniens': (115, 119),
        'Signes vitaux': (120, 124),
        'Complémentaires': (125, 139),
    }
    for cat, (start, end) in groups.items():
        actual_end = min(end + 1, len(SYMPTOMES_CANONIQUES))
        if start < len(SYMPTOMES_CANONIQUES):
            categories[cat] = SYMPTOMES_CANONIQUES[start:actual_end]

    # Ajouter les symptômes V2 qui dépassent l'index 139
    if len(SYMPTOMES_CANONIQUES) > 140:
        categories['Complémentaires V2'] = SYMPTOMES_CANONIQUES[140:]

    return categories


def get_maladies_canoniques() -> List[Dict[str, Any]]:
    """Retourne la liste des maladies avec catégorie et urgence."""
    return [
        {
            'nom': m['nom'],
            'categorie': m.get('categorie', ''),
            'urgence': bool(m.get('urgence', False)),
            'priorite_maroc': m.get('priorite_maroc', 'standard'),
        }
        for m in MALADIES
    ]

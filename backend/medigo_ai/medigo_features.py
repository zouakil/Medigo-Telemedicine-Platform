import numpy as np

from .medigo_kb_v2_complete import vectoriser_symptomes

PATIENT_FEATURE_NAMES = [
    'age',
    'sexe_homme',
    'sexe_femme',
    'grossesse',
    'temperature',
    'spo2',
    'bpm',
    'tension_systolique',
    'tension_diastolique',
    'glycemie',
    'antecedent_diabete',
    'antecedent_hta',
    'antecedent_cardiaque',
    'antecedent_asthme',
    'antecedent_bpco',
]


def safe_float(value, default=0.0):
    try:
        if value is None or value == '':
            return default
        return float(value)
    except Exception:
        return default


def extract_symptom_names(symptomes):
    names = []
    for item in symptomes or []:
        if isinstance(item, dict):
            nom = item.get('nom') or item.get('name') or item.get('symptome')
            if nom:
                names.append(str(nom))
        else:
            names.append(str(item))
    return names


def vectoriser_patient(patient, expected_num_symptom_features=None):
    symptomes = extract_symptom_names(patient.get('symptomes', []))
    x_symptomes = vectoriser_symptomes(
        symptomes=symptomes,
        vitaux={
            'temperature': patient.get('temperature'),
            'spo2': patient.get('spo2'),
            'fc': patient.get('bpm'),
            'ta_sys': patient.get('tension_systolique'),
            'ta_dia': patient.get('tension_diastolique'),
            'glycemie': patient.get('glycemie'),
        },
        as_numpy=True,
    )
    if expected_num_symptom_features is not None and len(x_symptomes) != expected_num_symptom_features:
        raise ValueError(f'Taille symptômes incompatible: {len(x_symptomes)} au lieu de {expected_num_symptom_features}')
    sexe = str(patient.get('sexe', '')).lower().strip()
    antecedents = patient.get('antecedents', {}) or {}
    x_patient = np.array([
        safe_float(patient.get('age')) / 100.0,
        1.0 if sexe in ['homme', 'm', 'male', 'masculin'] else 0.0,
        1.0 if sexe in ['femme', 'f', 'female', 'féminin', 'feminin'] else 0.0,
        1.0 if antecedents.get('grossesse') or patient.get('grossesse') else 0.0,
        safe_float(patient.get('temperature')) / 45.0,
        safe_float(patient.get('spo2')) / 100.0,
        safe_float(patient.get('bpm')) / 220.0,
        safe_float(patient.get('tension_systolique')) / 250.0,
        safe_float(patient.get('tension_diastolique')) / 150.0,
        safe_float(patient.get('glycemie')) / 6.0,
        1.0 if antecedents.get('diabete') else 0.0,
        1.0 if antecedents.get('hta') else 0.0,
        1.0 if antecedents.get('cardiaque') else 0.0,
        1.0 if antecedents.get('asthme') else 0.0,
        1.0 if antecedents.get('bpco') else 0.0,
    ], dtype=float)
    return np.concatenate([x_symptomes, x_patient])

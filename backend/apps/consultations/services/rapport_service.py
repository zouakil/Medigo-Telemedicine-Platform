"""
MEDIGO — Générateur de rapports de consultation (100% local)
À placer dans: backend/apps/consultations/services/rapport_service.py

Génère des textes médicaux structurés à partir des données Django.
Aucune donnée ne quitte le serveur.
"""
from datetime import date


def _age_texte(patient):
    if not patient.date_naissance:
        return ""
    today = date.today()
    age = today.year - patient.date_naissance.year
    if (today.month, today.day) < (patient.date_naissance.month, patient.date_naissance.day):
        age -= 1
    return f"{age} ans"


def _sexe_texte(patient):
    s = str(getattr(patient, 'sexe', '') or '').strip().upper()
    if s in ('M', 'H', 'HOMME', 'MASCULIN', 'MALE'):
        return 'M'
    elif s in ('F', 'FEMME', 'FEMININ', 'FÉMININ', 'FEMALE'):
        return 'F'
    return 'M'  # par défaut masculin si non précisé


def generer_rapport_consultation(consultation):
    """
    Génère un rapport médical structuré pour UNE consultation.
    Format visuel clair avec sections séparées.
    """
    from apps.consultations.models import (
        ConsultationSymptome, PatientMaladie, PatientAllergie,
        MesureAnthropo, InfoClinique
    )
    from apps.ordonnances.models import Ordonnance, OrdonnanceLigne

    patient = consultation.patient
    age = _age_texte(patient)
    sexe = _sexe_texte(patient)
    sexe_label = "Masculin" if sexe == "M" else "Féminin"

    # --- Symptômes ---
    symptomes = list(
        ConsultationSymptome.objects.filter(consultation=consultation)
        .values_list('nom_symptome', flat=True)
    )

    # --- Diagnostics retenus ---
    diagnostics_qs = PatientMaladie.objects.filter(consultation=consultation)
    diagnostics = []
    for d in diagnostics_qs:
        diag_info = {
            'nom': d.nom_maladie,
            'confiance': getattr(d, 'confiance_ia', None),
            'categorie': getattr(d, 'categorie', None),
        }
        diagnostics.append(diag_info)

    # --- Mesures ---
    mesure = MesureAnthropo.objects.filter(consultation=consultation).last()
    mesures_txt = []
    if mesure:
        if mesure.tension_sys and mesure.tension_dia:
            mesures_txt.append(f"TA {mesure.tension_sys}/{mesure.tension_dia} mmHg")
        if getattr(mesure, 'glycemie', None):
            mesures_txt.append(f"Glycémie {mesure.glycemie} g/L")
        if getattr(mesure, 'poids', None):
            mesures_txt.append(f"Poids {mesure.poids} kg")
        if getattr(mesure, 'taille', None):
            mesures_txt.append(f"Taille {mesure.taille} cm")

    # --- Info clinique ---
    try:
        info = InfoClinique.objects.get(consultation=consultation)
    except InfoClinique.DoesNotExist:
        info = None

    antecedents = []
    if info:
        if getattr(info, 'tabac', '') == 'fumeur':
            antecedents.append("Tabagisme actif")
        if getattr(info, 'alcool', '') == 'regulier':
            antecedents.append("Consommation alcool régulière")
        mc = getattr(info, 'maladies_chroniques', None)
        if mc and isinstance(mc, str) and mc.strip():
            antecedents.append(mc.strip())

    # Antécédents maladies chroniques
    chroniques = list(
        PatientMaladie.objects.filter(
            consultation__patient=patient,
            est_chronique=True
        ).values_list('nom_maladie', flat=True).distinct()
    )
    if chroniques:
        antecedents.extend(chroniques)

    # --- Allergies ---
    allergies = list(
        PatientAllergie.objects.filter(
            consultation__patient=patient
        ).values_list('nom_allergie', flat=True).distinct()
    )

    # --- Ordonnance ---
    # Les médicaments sont dans ordonnance.contenu (texte brut)
    medicaments = []
    try:
        ordo = Ordonnance.objects.filter(consultation=consultation).last()
        if ordo and ordo.contenu and ordo.contenu.strip():
            import re
            lines = ordo.contenu.strip().split('\n')
            current_med = None
            for line in lines:
                line_stripped = line.strip()
                if not line_stripped:
                    continue
                # Ligne de médicament principal (commence par chiffre. ou - ou •)
                if re.match(r'^(\d+\.\s*|[-•*]\s*)', line_stripped):
                    # Sauvegarder le médicament précédent
                    if current_med:
                        medicaments.append(current_med)
                    nom = re.sub(r'^(\d+\.\s*|[-•*]\s*)', '', line_stripped).strip()
                    current_med = {'nom': nom, 'posologie': '', 'duree': '', 'note': ''}
                elif current_med:
                    # Ligne de détail (posologie, durée, note)
                    if re.match(r'posologie\s*:', line_stripped, re.IGNORECASE):
                        current_med['posologie'] = re.sub(r'posologie\s*:\s*', '', line_stripped, flags=re.IGNORECASE).strip()
                    elif re.match(r'dur[eé]e\s*:', line_stripped, re.IGNORECASE):
                        current_med['duree'] = re.sub(r'dur[eé]e\s*:\s*', '', line_stripped, flags=re.IGNORECASE).strip()
                    elif re.match(r'note\s*:', line_stripped, re.IGNORECASE):
                        current_med['note'] = re.sub(r'note\s*:\s*', '', line_stripped, flags=re.IGNORECASE).strip()
                else:
                    # Pas de préfixe numérique mais c'est quand même un médicament
                    if current_med:
                        medicaments.append(current_med)
                    current_med = {'nom': line_stripped, 'posologie': '', 'duree': '', 'note': ''}
            # Ajouter le dernier médicament
            if current_med:
                medicaments.append(current_med)
    except Exception:
        pass

    # --- Red flags (si détectés pendant la consultation) ---
    red_flags = []
    # TODO: récupérer les red flags depuis les données de consultation si disponibles

    return {
        'patient_nom': f"{patient.prenom} {patient.nom}",
        'patient_age': age,
        'patient_sexe': sexe_label,
        'symptomes': symptomes,
        'diagnostics': diagnostics,
        'mesures': mesures_txt,
        'antecedents': antecedents,
        'allergies': allergies,
        'medicaments': medicaments,
        'red_flags': red_flags,
        'date': consultation.demarree_le or consultation.cloturee_le,
    }


def generer_resume_patient(patient):
    """
    Génère un résumé global combinant TOUTES les consultations d'un patient.
    100% local — aucune donnée ne sort du serveur.
    """
    from apps.consultations.models import (
        Consultation, ConsultationSymptome, PatientMaladie,
        PatientAllergie, InfoClinique
    )
    from apps.ordonnances.models import Ordonnance, OrdonnanceLigne

    age = _age_texte(patient)
    sexe = _sexe_texte(patient)

    # Toutes les consultations clôturées
    consultations = Consultation.objects.filter(
        patient=patient,
        statut='cloturee'
    ).order_by('-cloturee_le')

    nb_consultations = consultations.count()
    if nb_consultations == 0:
        return {
            'resume': f"Patient{'e' if sexe == 'féminin' else ''} de {age}, {sexe}. Aucune consultation enregistrée.",
            'nb_consultations': 0,
        }

    # Dernière consultation
    derniere = consultations.first()
    premiere = consultations.last()

    # Tous les diagnostics
    tous_diagnostics = list(
        PatientMaladie.objects.filter(
            consultation__patient=patient
        ).values_list('nom_maladie', flat=True)
    )
    diagnostics_uniques = list(dict.fromkeys(tous_diagnostics))  # ordre préservé, dédupliqué

    # Maladies chroniques
    chroniques = list(
        PatientMaladie.objects.filter(
            consultation__patient=patient,
            est_chronique=True
        ).values_list('nom_maladie', flat=True).distinct()
    )

    # Allergies
    allergies = list(
        PatientAllergie.objects.filter(
            consultation__patient=patient
        ).values_list('nom_allergie', flat=True).distinct()
    )

    # Symptômes récurrents (apparaissent dans > 1 consultation)
    from collections import Counter
    all_symptomes = list(
        ConsultationSymptome.objects.filter(
            consultation__patient=patient
        ).values_list('nom_symptome', flat=True)
    )
    symptome_counts = Counter(all_symptomes)
    recurrents = [s for s, c in symptome_counts.most_common(5) if c > 1]

    # Derniers médicaments
    derniers_meds = []
    try:
        ordo = Ordonnance.objects.filter(
            consultation__patient=patient
        ).order_by('-creee_le').first()
        if ordo:
            derniers_meds = list(
                OrdonnanceLigne.objects.filter(ordonnance=ordo)
                .values_list('medicament_nom', flat=True)
            )
    except Exception:
        pass

    # --- Construire le résumé ---
    phrases = []

    # Identité
    p = f"Patient{'e' if sexe == 'féminin' else ''} de {age}, {sexe}"
    if chroniques:
        p += f", suivi{'e' if sexe == 'féminin' else ''} pour {', '.join(chroniques[:3])}"
    p += "."
    phrases.append(p)

    if allergies:
        phrases.append(f"Allergies : {', '.join(allergies)}.")

    # Historique
    if nb_consultations == 1:
        phrases.append(f"Une seule consultation enregistrée le {derniere.cloturee_le.strftime('%d/%m/%Y') if derniere.cloturee_le else '?'}.")
    else:
        debut = premiere.cloturee_le.strftime('%d/%m/%Y') if premiere.cloturee_le else '?'
        fin = derniere.cloturee_le.strftime('%d/%m/%Y') if derniere.cloturee_le else '?'
        phrases.append(f"{nb_consultations} consultations enregistrées du {debut} au {fin}.")

    # Diagnostics
    if diagnostics_uniques:
        phrases.append(f"Pathologies diagnostiquées : {', '.join(diagnostics_uniques[:6])}.")

    # Symptômes récurrents
    if recurrents:
        phrases.append(f"Symptômes récurrents : {', '.join(recurrents)}.")

    # Traitement en cours
    if derniers_meds:
        meds_clean = [m for m in derniers_meds if m]
        if meds_clean:
            phrases.append(f"Dernier traitement prescrit : {', '.join(meds_clean[:5])}.")

    # Dernière consultation
    if derniere:
        derniers_symptomes = list(
            ConsultationSymptome.objects.filter(consultation=derniere)
            .values_list('nom_symptome', flat=True)
        )
        derniers_diags = list(
            PatientMaladie.objects.filter(consultation=derniere)
            .values_list('nom_maladie', flat=True)
        )
        if derniers_symptomes or derniers_diags:
            txt = f"Dernière consultation"
            if derniere.cloturee_le:
                txt += f" ({derniere.cloturee_le.strftime('%d/%m/%Y')})"
            txt += " : "
            if derniers_symptomes:
                txt += f"motif {', '.join(derniers_symptomes[:3]).lower()}"
            if derniers_diags:
                txt += f", diagnostic {'retenu' if len(derniers_diags)==1 else 'retenus'} : {', '.join(derniers_diags)}"
            txt += "."
            phrases.append(txt)

    return {
        'resume': ' '.join(phrases),
        'nb_consultations': nb_consultations,
        'diagnostics_uniques': diagnostics_uniques,
        'chroniques': chroniques,
        'allergies': allergies,
        'recurrents': recurrents,
        'derniers_meds': derniers_meds,
    }

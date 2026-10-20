"""
MEDIGO — Base de connaissances médicales pour le modèle XGBoost
60+ maladies, 200+ symptômes, red flags, questions contextuelles
Conçu pour la médecine générale en téléconsultation
"""

# ============================================================
# SYMPTÔMES CANONIQUES (français) — le modèle utilise ces noms
# Chaque symptôme a un ID numérique stable pour le vecteur XGBoost
# ============================================================

SYMPTOMES_CANONIQUES = [
    # Généraux (0-14)
    "Fièvre", "Fatigue", "Frissons", "Sueurs nocturnes", "Perte de poids",
    "Prise de poids", "Faiblesse générale", "Malaise", "Perte d'appétit", "Soif excessive",
    "Somnolence excessive", "Insomnie", "Irritabilité", "Anxiété", "Dépression",

    # Respiratoires (15-29)
    "Toux sèche", "Toux grasse", "Dyspnée", "Essoufflement", "Sifflements respiratoires",
    "Hémoptysie", "Douleur thoracique", "Obstruction nasale", "Rhinorrhée", "Éternuements",
    "Enrouement", "Toux", "Cyanose", "Douleur pleurale", "Expectoration purulente",

    # Digestifs (30-44)
    "Nausées", "Vomissements", "Diarrhée", "Constipation", "Douleurs abdominales",
    "Ballonnements", "Brûlures d'estomac", "Reflux gastrique", "Dysphagie", "Sang dans les selles",
    "Jaunisse", "Perte d'appétit digestive", "Crampes abdominales", "Selles graisseuses", "Ténesme",

    # Urinaires (45-54)
    "Brûlures mictionnelles", "Mictions fréquentes", "Sang dans les urines", "Incontinence urinaire",
    "Douleurs lombaires", "Oligurie", "Polyurie", "Nycturie", "Urine foncée", "Urine trouble",

    # Cardio-vasculaires (55-64)
    "Palpitations", "Douleur à l'effort", "Douleur au repos", "Œdème des membres inférieurs",
    "Varices", "Claudication intermittente", "Syncope", "Lipothymie", "Hypotension", "Hypertension",

    # Neurologiques (65-79)
    "Maux de tête", "Vertiges", "Étourdissements", "Confusion", "Perte de conscience",
    "Convulsions", "Tremblements", "Engourdissements", "Fourmillements", "Faiblesse musculaire",
    "Troubles de la vision", "Troubles de la mémoire", "Photophobie", "Raideur de la nuque",
    "Troubles de l'élocution",

    # Musculo-squelettiques (80-89)
    "Douleurs articulaires", "Douleurs musculaires", "Raideur matinale", "Gonflement articulaire",
    "Douleurs osseuses", "Crampes musculaires", "Limitation mobilité", "Douleur rachidienne",
    "Sciatique", "Douleur cervicale",

    # Dermatologiques (90-99)
    "Éruption cutanée", "Démangeaisons", "Rougeurs", "Urticaire", "Lésions cutanées",
    "Alopécie", "Ecchymoses faciles", "Pâleur", "Desquamation", "Vésicules",

    # ORL (100-109)
    "Douleurs pharyngées", "Douleurs auriculaires", "Acouphènes", "Anosmie", "Ageusie",
    "Epistaxis", "Adénopathies", "Dysphagie ORL", "Otorrhée", "Vertiges positionnels",

    # Gynécologiques (110-114)
    "Douleurs pelviennes", "Aménorrhée", "Dysménorrhée", "Saignements vaginaux",
    "Leucorrhées",

    # Endocriniens (115-119)
    "Polydipsie", "Polyphagie", "Goitre", "Exophtalmie", "Intolérance chaleur",

    # Signes vitaux anormaux (120-124) — viennent des capteurs
    "Tachycardie", "Bradycardie", "Hypoxie", "Hyperthermie", "Hypothermie",

    # Complémentaires (125-139)
    "Œdème", "Gonflement visage", "Saignements anormaux", "Hématurie", "Asthénie",
    "Myalgies diffuses", "Arthralgies migratrices", "Prurit généralisé", "Ictère",
    "Hépatomégalie", "Splénomégalie", "Ascite", "Tachypnée", "Wheezing", "Stridor",
]

# Index rapide
SYMPTOME_TO_IDX = {s: i for i, s in enumerate(SYMPTOMES_CANONIQUES)}
NUM_FEATURES = len(SYMPTOMES_CANONIQUES)

# ============================================================
# MALADIES — chaque maladie avec ses symptômes associés et poids
# Format: (nom_maladie, {symptôme: probabilité 0-1}, catégorie, red_flags, questions)
# ============================================================

MALADIES = [
    # ---- RESPIRATOIRES ----
    {
        "nom": "Grippe / Syndrome grippal",
        "categorie": "respiratoire",
        "symptomes": {
            "Fièvre": 0.95, "Frissons": 0.85, "Fatigue": 0.90, "Maux de tête": 0.80,
            "Douleurs musculaires": 0.85, "Toux sèche": 0.70, "Rhinorrhée": 0.60,
            "Douleurs pharyngées": 0.55, "Perte d'appétit": 0.50, "Faiblesse générale": 0.80,
            "Myalgies diffuses": 0.75, "Sueurs nocturnes": 0.40, "Asthénie": 0.70,
        },
        "red_flags": ["Dyspnée sévère", "Confusion", "SpO2 < 92%"],
        "questions": ["Début brutal ou progressif ?", "Contact avec un cas confirmé ?",
                       "Vacciné cette saison ?", "Depuis combien de jours ?"],
    },
    {
        "nom": "Rhinopharyngite / Rhume",
        "categorie": "respiratoire",
        "symptomes": {
            "Rhinorrhée": 0.95, "Obstruction nasale": 0.90, "Éternuements": 0.80,
            "Douleurs pharyngées": 0.60, "Toux sèche": 0.50, "Fièvre": 0.30,
            "Fatigue": 0.40, "Maux de tête": 0.35,
        },
        "red_flags": ["Fièvre > 39°C persistante > 3 jours"],
        "questions": ["Rhinorrhée claire ou purulente ?", "Depuis combien de jours ?"],
    },
    {
        "nom": "Pneumonie",
        "categorie": "respiratoire",
        "symptomes": {
            "Fièvre": 0.90, "Toux grasse": 0.85, "Dyspnée": 0.80, "Douleur thoracique": 0.65,
            "Frissons": 0.70, "Fatigue": 0.75, "Expectoration purulente": 0.70,
            "Tachycardie": 0.60, "Essoufflement": 0.80, "Sueurs nocturnes": 0.50,
            "Hypoxie": 0.55, "Tachypnée": 0.65, "Douleur pleurale": 0.50,
        },
        "red_flags": ["SpO2 < 92%", "Confusion", "Tension basse", "FR > 30/min"],
        "questions": ["Expectoration : couleur et quantité ?", "Douleur latéralisée ?",
                       "Antécédent pulmonaire ?", "Tabagisme ?"],
    },
    {
        "nom": "Bronchite aiguë",
        "categorie": "respiratoire",
        "symptomes": {
            "Toux": 0.95, "Toux grasse": 0.70, "Fièvre": 0.40, "Fatigue": 0.50,
            "Douleur thoracique": 0.10, "Rhinorrhée": 0.40, "Douleurs pharyngées": 0.35,
            "Essoufflement": 0.15, "Expectoration purulente": 0.40,
        },
        "red_flags": ["Dyspnée sévère", "Fièvre > 39°C > 3j"],
        "questions": ["Toux depuis combien de jours ?", "Tabagisme ?", "BPCO connue ?"],
    },
    {
        "nom": "Asthme (crise)",
        "categorie": "respiratoire",
        "symptomes": {
            "Sifflements respiratoires": 0.95, "Dyspnée": 0.90, "Toux sèche": 0.70,
            "Essoufflement": 0.85, "Douleur thoracique": 0.30, "Wheezing": 0.90,
            "Tachycardie": 0.50, "Anxiété": 0.40, "Tachypnée": 0.60,
        },
        "red_flags": ["Impossibilité de parler", "Cyanose", "SpO2 < 90%", "Silence auscultatoire"],
        "questions": ["Asthme connu ?", "Traitement de fond ?", "Facteur déclenchant identifié ?"],
    },
    {
        "nom": "COVID-19",
        "categorie": "respiratoire",
        "symptomes": {
            "Fièvre": 0.80, "Toux sèche": 0.75, "Fatigue": 0.85, "Anosmie": 0.70,
            "Ageusie": 0.65, "Dyspnée": 0.55, "Maux de tête": 0.60, "Douleurs musculaires": 0.65,
            "Diarrhée": 0.30, "Douleurs pharyngées": 0.40, "Frissons": 0.50,
            "Rhinorrhée": 0.35, "Hypoxie": 0.40,
        },
        "red_flags": ["SpO2 < 94%", "Dyspnée au repos", "Confusion"],
        "questions": ["Contact cas confirmé ?", "Vacciné ?", "Perte goût/odorat ?", "Depuis combien de jours ?"],
    },
    {
        "nom": "BPCO (exacerbation)",
        "categorie": "respiratoire",
        "symptomes": {
            "Dyspnée": 0.95, "Toux grasse": 0.85, "Expectoration purulente": 0.80,
            "Essoufflement": 0.90, "Sifflements respiratoires": 0.60, "Wheezing": 0.55,
            "Cyanose": 0.40, "Fatigue": 0.70, "Tachypnée": 0.50, "Hypoxie": 0.50,
        },
        "red_flags": ["SpO2 < 88%", "Confusion", "Cyanose"],
        "questions": ["BPCO connue ? Stade ?", "Tabagisme actif ?", "Combien de paquets-année ?"],
    },
    {
        "nom": "Angine / Pharyngite",
        "categorie": "ORL",
        "symptomes": {
            "Douleurs pharyngées": 0.95, "Fièvre": 0.75, "Dysphagie": 0.70,
            "Adénopathies": 0.65, "Maux de tête": 0.40, "Fatigue": 0.50,
            "Frissons": 0.35,
        },
        "red_flags": ["Trismus", "Dyspnée", "Voix étouffée (phlegmon)"],
        "questions": ["Douleur unilatérale ou bilatérale ?", "Points blancs amygdales ?",
                       "Score de McIsaac ?"],
    },
    {
        "nom": "Sinusite",
        "categorie": "ORL",
        "symptomes": {
            "Obstruction nasale": 0.90, "Douleurs faciales": 0.85, "Rhinorrhée": 0.80,
            "Maux de tête": 0.70, "Fièvre": 0.50, "Anosmie": 0.40,
            "Toux": 0.35, "Douleurs auriculaires": 0.25,
        },
        "red_flags": ["Œdème périorbitaire", "Troubles visuels", "Fièvre > 39°C"],
        "questions": ["Douleur augmentée en se penchant ?", "Rhinorrhée purulente ?",
                       "Depuis plus de 10 jours ?"],
    },
    {
        "nom": "Otite moyenne aiguë",
        "categorie": "ORL",
        "symptomes": {
            "Douleurs auriculaires": 0.95, "Fièvre": 0.70, "Otorrhée": 0.40,
            "Maux de tête": 0.35, "Vertiges": 0.20, "Acouphènes": 0.25,
            "Irritabilité": 0.30,
        },
        "red_flags": ["Mastoïdite (rougeur rétro-auriculaire)", "Paralysie faciale"],
        "questions": ["Oreille gauche ou droite ?", "Écoulement ?", "Baignade récente ?"],
    },

    # ---- DIGESTIFS ----
    {
        "nom": "Gastro-entérite aiguë",
        "categorie": "digestif",
        "symptomes": {
            "Diarrhée": 0.95, "Nausées": 0.85, "Vomissements": 0.80, "Douleurs abdominales": 0.75,
            "Fièvre": 0.50, "Crampes abdominales": 0.70, "Fatigue": 0.60,
            "Perte d'appétit": 0.65, "Frissons": 0.30,
        },
        "red_flags": ["Déshydratation sévère", "Sang dans les selles", "Fièvre > 39°C > 48h"],
        "questions": ["Depuis quand ?", "Nombre de selles/jour ?", "Sang ou glaires ?",
                       "Voyage récent ?", "Repas suspect ?"],
    },
    {
        "nom": "Reflux gastro-œsophagien",
        "categorie": "digestif",
        "symptomes": {
            "Brûlures d'estomac": 0.95, "Reflux gastrique": 0.90, "Douleur thoracique": 0.40,
            "Toux sèche": 0.30, "Dysphagie": 0.25, "Nausées": 0.30,
            "Enrouement": 0.20, "Ballonnements": 0.35,
        },
        "red_flags": ["Dysphagie progressive", "Perte de poids", "Anémie", "Hématémèse"],
        "questions": ["Aggravé en position allongée ?", "Après les repas ?",
                       "Prise d'AINS ou aspirine ?"],
    },
    {
        "nom": "Appendicite",
        "categorie": "digestif",
        "symptomes": {
            "Douleurs abdominales": 0.95,
            "Défense abdominale": 0.95,
            "Nausées": 0.70,
            "Vomissements": 0.60,
            "Fièvre": 0.65,
            "Perte d'appétit": 0.85,
            "Constipation": 0.25,
            "Diarrhée": 0.10,
            "Tachycardie": 0.35,
        },
        "red_flags": [
            "Défense abdominale",
            "Douleur FID typique",
            "Fièvre + tachycardie",
            "Contracture abdominale"
        ],
        "questions": [
            "Douleur commencée où ? Migré ?",
            "Douleur fosse iliaque droite ?",
            "Point de McBurney ?",
            "Fièvre associée ?",
            "Défense ou douleur à la décompression ?"
        ],
    },
    {
        "nom": "Cholécystite",
        "categorie": "digestif",
        "symptomes": {
            "Douleurs abdominales": 0.90, "Nausées": 0.75, "Vomissements": 0.65,
            "Fièvre": 0.70, "Jaunisse": 0.30, "Perte d'appétit": 0.55,
            "Ballonnements": 0.40, "Ictère": 0.25,
        },
        "red_flags": ["Fièvre + ictère + douleur (triade de Charcot)", "Défense HCD"],
        "questions": ["Douleur hypochondre droit ?", "Après repas gras ?",
                       "Antécédent de calculs ?"],
    },
    {
        "nom": "Ulcère gastroduodénal",
        "categorie": "digestif",
        "symptomes": {
            "Brûlures d'estomac": 0.90,
            "Douleurs abdominales": 0.75,
            "Nausées": 0.40,
            "Vomissements": 0.25,
            "Perte d'appétit": 0.35,
            "Sang dans les selles": 0.25,
            "Perte de poids": 0.25,
            "Ballonnements": 0.35,
        },
        "red_flags": ["Hématémèse", "Méléna", "Douleur en coup de poignard (perforation)"],
        "questions": ["Douleur soulagée par le repas ?", "Prise d'AINS ?", "Antécédent H. pylori ?"],
    },
    {
        "nom": "Syndrome du côlon irritable",
        "categorie": "digestif",
        "symptomes": {
            "Douleurs abdominales": 0.90, "Ballonnements": 0.85, "Diarrhée": 0.60,
            "Constipation": 0.60, "Crampes abdominales": 0.75, "Nausées": 0.30,
            "Fatigue": 0.40, "Anxiété": 0.35,
        },
        "red_flags": ["Sang dans les selles", "Perte de poids", "Anémie", "Début > 50 ans"],
        "questions": ["Alternance diarrhée/constipation ?", "Stress/anxiété ?",
                       "Symptômes nocturnes ?"],
    },
    {
        "nom": "Hépatite aiguë",
        "categorie": "digestif",
        "symptomes": {
            "Jaunisse": 0.85, "Ictère": 0.85, "Fatigue": 0.90, "Nausées": 0.70,
            "Douleurs abdominales": 0.55, "Perte d'appétit": 0.80, "Urine foncée": 0.75,
            "Fièvre": 0.40, "Vomissements": 0.45, "Douleurs articulaires": 0.30,
            "Hépatomégalie": 0.50,
        },
        "red_flags": ["Encéphalopathie hépatique", "INR élevé", "Hémorragie"],
        "questions": ["Voyage récent ?", "Transfusion ?", "Consommation d'alcool ?",
                       "Médicaments hépatotoxiques ?"],
    },

    # ---- URINAIRES ----
    {
        "nom": "Infection urinaire basse / Cystite",
        "categorie": "urinaire",
        "symptomes": {
            "Brûlures mictionnelles": 0.98,
            "Mictions fréquentes": 0.95,
            "Urine trouble": 0.75,
            "Douleurs pelviennes": 0.45,
            "Sang dans les urines": 0.30,
            "Nycturie": 0.35,
        },
        "red_flags": ["Fièvre (= pyélonéphrite)", "Douleurs lombaires"],
        "questions": ["Première infection ?", "Grossesse ?", "Diabète ?", "IST récente ?"],
    },
    {
        "nom": "Pyélonéphrite",
        "categorie": "urinaire",
        "symptomes": {
            "Fièvre": 0.95, "Douleurs lombaires": 0.90, "Frissons": 0.80,
            "Brûlures mictionnelles": 0.60, "Nausées": 0.55, "Vomissements": 0.45,
            "Fatigue": 0.70, "Mictions fréquentes": 0.50, "Tachycardie": 0.40,
        },
        "red_flags": ["Sepsis", "Anurie", "Terrain immunodéprimé"],
        "questions": ["Douleur latéralisée ?", "Cystite préalable ?",
                       "Antécédent de lithiase ?"],
    },
    {
        "nom": "Colique néphrétique",
        "categorie": "urinaire",
        "symptomes": {
            "Douleurs lombaires": 0.95, "Nausées": 0.70, "Vomissements": 0.60,
            "Sang dans les urines": 0.50, "Hématurie": 0.50, "Mictions fréquentes": 0.35,
            "Douleurs abdominales": 0.40, "Agitation": 0.65,
        },
        "red_flags": ["Fièvre (= urgence chirurgicale)", "Anurie", "Rein unique"],
        "questions": ["Douleur irradiant vers les OGE ?", "Antécédent de calculs ?",
                       "Hydratation habituelle ?"],
    },

    # ---- CARDIOVASCULAIRES ----
    {
        "nom": "Insuffisance cardiaque",
        "categorie": "cardiovasculaire",
        "symptomes": {
            "Dyspnée": 0.95, "Œdème des membres inférieurs": 0.85, "Fatigue": 0.80,
            "Essoufflement": 0.90, "Prise de poids": 0.50, "Toux sèche": 0.35,
            "Palpitations": 0.40, "Nycturie": 0.45, "Œdème": 0.70,
            "Orthopnée": 0.65, "Tachycardie": 0.50,
        },
        "red_flags": ["OAP", "SpO2 < 90%", "Choc cardiogénique"],
        "questions": ["Dyspnée d'effort ou de repos ?", "Combien d'oreillers la nuit ?",
                       "Prise de poids récente rapide ?"],
    },
    {
        "nom": "Hypertension artérielle",
        "categorie": "cardiovasculaire",
        "symptomes": {
            "Maux de tête": 0.60, "Vertiges": 0.45, "Étourdissements": 0.40,
            "Palpitations": 0.35, "Essoufflement": 0.30, "Epistaxis": 0.25,
            "Troubles de la vision": 0.30, "Acouphènes": 0.20, "Hypertension": 0.95,
        },
        "red_flags": ["HTA maligne (> 180/120)", "Céphalée violente", "Troubles visuels"],
        "questions": ["HTA connue ?", "Traitement en cours ?", "Observance ?",
                       "Mesures habituelles ?"],
    },
    {
        "nom": "Angor / Angine de poitrine",
        "categorie": "cardiovasculaire",
        "symptomes": {
            "Douleur thoracique": 0.95, "Douleur à l'effort": 0.85, "Essoufflement": 0.60,
            "Palpitations": 0.35, "Sueurs nocturnes": 0.30, "Anxiété": 0.40,
            "Nausées": 0.25, "Dyspnée": 0.50,
        },
        "red_flags": ["Douleur au repos (angor instable = SCA)", "Irradiation mâchoire/bras gauche",
                       "Sueurs froides"],
        "questions": ["Douleur rétrosternale constrictive ?", "Soulagée par le repos ?",
                       "Facteurs de risque CV ?", "Durée de la douleur ?"],
    },
    {
        "nom": "Embolie pulmonaire",
        "categorie": "cardiovasculaire",
        "symptomes": {
            "Dyspnée": 0.90, "Douleur thoracique": 0.75, "Tachycardie": 0.80,
            "Hémoptysie": 0.30, "Toux": 0.35, "Douleur pleurale": 0.60,
            "Syncope": 0.20, "Œdème des membres inférieurs": 0.35, "Anxiété": 0.50,
            "Hypoxie": 0.65, "Tachypnée": 0.70,
        },
        "red_flags": ["URGENCE VITALE", "Choc", "SpO2 effondrée"],
        "questions": ["Immobilisation récente ?", "Chirurgie récente ?",
                       "Contraception orale ?", "Voyage long trajet ?",
                       "Antécédent thromboembolique ?"],
    },
    {
        "nom": "Thrombose veineuse profonde",
        "categorie": "cardiovasculaire",
        "symptomes": {
            "Œdème des membres inférieurs": 0.90, "Douleur au repos": 0.70,
            "Rougeurs": 0.55, "Crampes musculaires": 0.40, "Douleur à l'effort": 0.35,
            "Pâleur": 0.20,
        },
        "red_flags": ["Embolie pulmonaire secondaire", "Phlegmatia"],
        "questions": ["Mollet douloureux et tendu ?", "Facteurs de risque (immobilisation, chirurgie, cancer) ?",
                       "Signe de Homans ?"],
    },

    # ---- NEUROLOGIQUES ----
    {
        "nom": "Migraine",
        "categorie": "neurologique",
        "symptomes": {
            "Maux de tête": 0.95, "Nausées": 0.70, "Vomissements": 0.50,
            "Photophobie": 0.75, "Troubles de la vision": 0.40, "Fatigue": 0.50,
            "Vertiges": 0.25, "Irritabilité": 0.30,
        },
        "red_flags": ["Céphalée brutale en coup de tonnerre", "Déficit neurologique",
                       "Première crise > 50 ans"],
        "questions": ["Unilatérale ou bilatérale ?", "Pulsatile ?", "Aura ?",
                       "Fréquence des crises ?", "Facteurs déclenchants ?"],
    },
    {
        "nom": "Céphalée de tension",
        "categorie": "neurologique",
        "symptomes": {
            "Maux de tête": 0.95, "Fatigue": 0.50, "Anxiété": 0.45,
            "Insomnie": 0.35, "Douleur cervicale": 0.40, "Irritabilité": 0.30,
        },
        "red_flags": ["Fièvre associée", "Déficit neurologique"],
        "questions": ["En casque ou en bandeau ?", "Bilatérale ?", "Stress ou tension cervicale ?"],
    },
    {
        "nom": "AVC / AIT",
        "categorie": "neurologique",
        "symptomes": {
            "Faiblesse musculaire": 0.85, "Troubles de l'élocution": 0.80,
            "Troubles de la vision": 0.60, "Confusion": 0.65, "Maux de tête": 0.50,
            "Vertiges": 0.55, "Engourdissements": 0.70, "Perte de conscience": 0.30,
        },
        "red_flags": ["URGENCE VITALE — appeler le 15/SAMU immédiatement",
                       "Hémiplégie", "Aphasie", "Asymétrie faciale"],
        "questions": ["Début brutal ?", "Heure de début des symptômes ?",
                       "Déficit latéralisé ?", "Antécédent CV ?"],
    },
    {
        "nom": "Méningite",
        "categorie": "neurologique",
        "symptomes": {
            "Maux de tête": 0.95, "Fièvre": 0.90, "Raideur de la nuque": 0.85,
            "Photophobie": 0.70, "Nausées": 0.65, "Vomissements": 0.60,
            "Confusion": 0.50, "Convulsions": 0.30, "Éruption cutanée": 0.25,
            "Pâleur": 0.30,
        },
        "red_flags": ["URGENCE VITALE", "Purpura fulminans", "Troubles de conscience"],
        "questions": ["Raideur de la nuque ?", "Purpura ?", "Contage méningocoque ?"],
    },
    {
        "nom": "Vertige paroxystique positionnel bénin (VPPB)",
        "categorie": "neurologique",
        "symptomes": {
            "Vertiges positionnels": 0.95, "Vertiges": 0.90, "Nausées": 0.65,
            "Vomissements": 0.40, "Étourdissements": 0.50,
        },
        "red_flags": ["Déficit neurologique associé", "Surdité brutale"],
        "questions": ["Vertiges au changement de position ?", "Durée des épisodes ?",
                       "Nystagmus ?"],
    },

    # ---- ENDOCRINIENS ----
    {
        "nom": "Diabète (décompensation)",
        "categorie": "endocrinien",
        "symptomes": {
            "Polydipsie": 0.90, "Polyurie": 0.85, "Polyphagie": 0.65,
            "Perte de poids": 0.70, "Fatigue": 0.80, "Troubles de la vision": 0.40,
            "Soif excessive": 0.90, "Mictions fréquentes": 0.80, "Nausées": 0.30,
        },
        "red_flags": ["Acidocétose (haleine acétonique, polypnée)", "Coma"],
        "questions": ["Diabète connu ?", "Glycémie récente ?", "Traitement en cours ?",
                       "Prise de poids ou perte de poids ?"],
    },
    {
        "nom": "Hyperthyroïdie",
        "categorie": "endocrinien",
        "symptomes": {
            "Palpitations": 0.85, "Perte de poids": 0.80, "Tremblements": 0.75,
            "Tachycardie": 0.80, "Anxiété": 0.65, "Intolérance chaleur": 0.70,
            "Sueurs nocturnes": 0.55, "Diarrhée": 0.40, "Insomnie": 0.60,
            "Fatigue": 0.50, "Exophtalmie": 0.35, "Goitre": 0.45,
            "Irritabilité": 0.55,
        },
        "red_flags": ["Crise thyréotoxique", "AC/FA", "Insuffisance cardiaque"],
        "questions": ["Thyroïde connue ?", "Palpitation de la thyroïde ?",
                       "Troubles du cycle menstruel ?"],
    },
    {
        "nom": "Hypothyroïdie",
        "categorie": "endocrinien",
        "symptomes": {
            "Fatigue": 0.90, "Prise de poids": 0.75, "Constipation": 0.65,
            "Pâleur": 0.40, "Bradycardie": 0.50, "Dépression": 0.45,
            "Crampes musculaires": 0.40, "Alopécie": 0.35, "Douleurs musculaires": 0.30,
            "Somnolence excessive": 0.55, "Goitre": 0.30, "Raideur matinale": 0.25,
        },
        "red_flags": ["Coma myxœdémateux", "Bradycardie sévère"],
        "questions": ["TSH récente ?", "Traitement substitutif ?", "Thyroïdectomie ?"],
    },

    # ---- DERMATOLOGIQUES ----
    {
        "nom": "Eczéma / Dermatite atopique",
        "categorie": "dermatologique",
        "symptomes": {
            "Démangeaisons": 0.95, "Éruption cutanée": 0.85, "Rougeurs": 0.80,
            "Desquamation": 0.60, "Lésions cutanées": 0.65, "Insomnie": 0.30,
        },
        "red_flags": ["Surinfection (suintement, croûtes mélicériques)"],
        "questions": ["Terrain atopique ?", "Localisation ?", "Facteurs aggravants ?"],
    },
    {
        "nom": "Urticaire",
        "categorie": "dermatologique",
        "symptomes": {
            "Urticaire": 0.95, "Démangeaisons": 0.90, "Rougeurs": 0.75,
            "Œdème": 0.40, "Gonflement visage": 0.30, "Anxiété": 0.20,
        },
        "red_flags": ["Œdème de Quincke", "Dyspnée (anaphylaxie)", "Choc"],
        "questions": ["Aliment ou médicament nouveau ?", "Piqûre d'insecte ?",
                       "Signes respiratoires associés ?"],
    },
    {
        "nom": "Zona",
        "categorie": "dermatologique",
        "symptomes": {
            "Éruption cutanée": 0.90, "Douleur au repos": 0.85, "Vésicules": 0.85,
            "Démangeaisons": 0.50, "Fièvre": 0.30, "Fatigue": 0.40,
            "Maux de tête": 0.25, "Lésions cutanées": 0.70,
        },
        "red_flags": ["Zona ophtalmique", "Zona chez immunodéprimé"],
        "questions": ["Distribution métamérique ?", "Unilatéral ?",
                       "Antécédent de varicelle ?", "Immunodépression ?"],
    },

    # ---- RHUMATOLOGIQUES ----
    {
        "nom": "Polyarthrite rhumatoïde",
        "categorie": "rhumatologique",
        "symptomes": {
            "Douleurs articulaires": 0.95, "Raideur matinale": 0.90,
            "Gonflement articulaire": 0.85, "Fatigue": 0.70, "Fièvre": 0.30,
            "Perte de poids": 0.25, "Douleurs musculaires": 0.35,
            "Limitation mobilité": 0.60, "Arthralgies migratrices": 0.40,
        },
        "red_flags": ["Atteinte extra-articulaire (poumon, cœur)", "Vascularite"],
        "questions": ["Raideur matinale > 30 min ?", "Articulations atteintes ?",
                       "Symétrique ?", "Antécédent familial ?"],
    },
    {
        "nom": "Goutte (crise)",
        "categorie": "rhumatologique",
        "symptomes": {
            "Douleurs articulaires": 0.95, "Gonflement articulaire": 0.90,
            "Rougeurs": 0.80, "Fièvre": 0.40, "Limitation mobilité": 0.60,
            "Douleur au repos": 0.50,
        },
        "red_flags": ["Arthrite septique (à éliminer)"],
        "questions": ["Premier épisode ?", "Articulation touchée (MTP1) ?",
                       "Acide urique connu ?", "Alimentation récente (viande, alcool) ?"],
    },
    {
        "nom": "Lombalgie aiguë / Lumbago",
        "categorie": "rhumatologique",
        "symptomes": {
            "Douleurs lombaires": 0.95, "Limitation mobilité": 0.80,
            "Douleur rachidienne": 0.85, "Crampes musculaires": 0.50,
            "Sciatique": 0.35, "Douleurs musculaires": 0.40,
        },
        "red_flags": ["Syndrome de la queue de cheval", "Déficit moteur",
                       "Fièvre (spondylodiscite)", "Perte de poids"],
        "questions": ["Effort déclenchant ?", "Irradiation dans les jambes ?",
                       "Troubles sphinctériens ?"],
    },
    {
        "nom": "Sciatique / Hernie discale",
        "categorie": "rhumatologique",
        "symptomes": {
            "Sciatique": 0.95, "Douleurs lombaires": 0.85, "Engourdissements": 0.60,
            "Fourmillements": 0.55, "Faiblesse musculaire": 0.45,
            "Douleur rachidienne": 0.50, "Limitation mobilité": 0.55,
        },
        "red_flags": ["Syndrome de la queue de cheval (urgence)", "Déficit moteur",
                       "Troubles sphinctériens"],
        "questions": ["Trajet L5 ou S1 ?", "Lasègue positif ?",
                       "Déficit sensitif ou moteur ?"],
    },

    # ---- INFECTIEUX ----
    {
        "nom": "Paludisme / Malaria",
        "categorie": "infectieux",
        "symptomes": {
            "Fièvre": 0.95, "Frissons": 0.90, "Sueurs nocturnes": 0.80,
            "Maux de tête": 0.75, "Fatigue": 0.80, "Nausées": 0.55,
            "Vomissements": 0.50, "Douleurs musculaires": 0.60, "Diarrhée": 0.30,
            "Jaunisse": 0.25, "Splénomégalie": 0.40, "Pâleur": 0.35,
        },
        "red_flags": ["Paludisme grave (confusion, convulsions, ictère, anémie sévère)"],
        "questions": ["Voyage en zone endémique ?", "Quand ?", "Prophylaxie prise ?",
                       "Fièvre cyclique ?"],
    },
    {
        "nom": "Mononucléose infectieuse",
        "categorie": "infectieux",
        "symptomes": {
            "Fatigue": 0.95, "Fièvre": 0.85, "Douleurs pharyngées": 0.80,
            "Adénopathies": 0.90, "Maux de tête": 0.45, "Splénomégalie": 0.40,
            "Éruption cutanée": 0.25, "Asthénie": 0.80,
        },
        "red_flags": ["Rupture de rate", "Obstruction des voies aériennes"],
        "questions": ["Adolescent/jeune adulte ?", "Contact avec cas ?",
                       "Éruption après amoxicilline ?"],
    },
    {
        "nom": "Tuberculose",
        "categorie": "infectieux",
        "symptomes": {
            "Toux": 0.90, "Toux grasse": 0.70, "Hémoptysie": 0.40,
            "Sueurs nocturnes": 0.80, "Perte de poids": 0.75, "Fièvre": 0.70,
            "Fatigue": 0.85, "Perte d'appétit": 0.60, "Dyspnée": 0.35,
            "Asthénie": 0.70,
        },
        "red_flags": ["Hémoptysie massive", "Miliaire"],
        "questions": ["Contage tuberculeux ?", "Voyage/origine zone endémique ?",
                       "Immunodépression ?", "BCG ?"],
    },

    # ---- HÉMATOLOGIQUES ----
    {
        "nom": "Anémie",
        "categorie": "hématologique",
        "symptomes": {
            "Fatigue": 0.95, "Pâleur": 0.85, "Dyspnée": 0.60, "Essoufflement": 0.65,
            "Palpitations": 0.55, "Tachycardie": 0.50, "Vertiges": 0.45,
            "Maux de tête": 0.35, "Faiblesse générale": 0.70,
            "Étourdissements": 0.40, "Asthénie": 0.80,
        },
        "red_flags": ["Anémie sévère (Hb < 7g/dL)", "Saignement actif", "Détresse respiratoire"],
        "questions": ["Régime alimentaire ?", "Saignements (règles, digestif) ?",
                       "Pica ?", "Végétarien ?"],
    },

    # ---- PSYCHIATRIQUES ----
    {
        "nom": "Trouble anxieux généralisé",
        "categorie": "psychiatrique",
        "symptomes": {
            "Anxiété": 0.95, "Insomnie": 0.75, "Fatigue": 0.65, "Irritabilité": 0.60,
            "Palpitations": 0.55, "Tremblements": 0.40, "Maux de tête": 0.45,
            "Douleurs musculaires": 0.35, "Diarrhée": 0.25, "Nausées": 0.30,
            "Essoufflement": 0.30, "Vertiges": 0.25,
        },
        "red_flags": ["Idéation suicidaire", "Attaque de panique avec douleur thoracique"],
        "questions": ["Depuis quand ?", "Facteurs déclenchants ?",
                       "Retentissement sur le quotidien ?", "Traitement en cours ?"],
    },
    {
        "nom": "Épisode dépressif",
        "categorie": "psychiatrique",
        "symptomes": {
            "Dépression": 0.95, "Insomnie": 0.75, "Fatigue": 0.85,
            "Perte d'appétit": 0.60, "Perte de poids": 0.45, "Anxiété": 0.55,
            "Troubles de la mémoire": 0.40, "Irritabilité": 0.45,
            "Somnolence excessive": 0.35, "Douleurs musculaires": 0.25,
        },
        "red_flags": ["Idéation suicidaire", "Plan suicidaire", "Symptômes psychotiques"],
        "questions": ["Depuis quand ?", "Événement déclencheur ?",
                       "Idées noires ?", "Perte d'intérêt et de plaisir ?"],
    },

    # ---- ALLERGIQUES ----
    {
        "nom": "Rhinite allergique",
        "categorie": "allergique",
        "symptomes": {
            "Rhinorrhée": 0.90, "Éternuements": 0.90, "Obstruction nasale": 0.80,
            "Démangeaisons": 0.60, "Rougeur oculaire": 0.55, "Larmoiement": 0.50,
            "Maux de tête": 0.25,
        },
        "red_flags": ["Asthme associé non contrôlé"],
        "questions": ["Saisonnier ou perannuel ?", "Terrain atopique ?",
                       "Animaux de compagnie ?"],
    },
    {
        "nom": "Choc anaphylactique",
        "categorie": "allergique",
        "symptomes": {
            "Urticaire": 0.80, "Dyspnée": 0.85, "Hypotension": 0.80,
            "Tachycardie": 0.75, "Gonflement visage": 0.70, "Œdème": 0.65,
            "Pâleur": 0.50, "Nausées": 0.45, "Vomissements": 0.40,
            "Confusion": 0.35, "Syncope": 0.30, "Anxiété": 0.55,
        },
        "red_flags": ["URGENCE VITALE ABSOLUE", "Adrénaline IM immédiate"],
        "questions": ["Allergène identifié ?", "Antécédent d'anaphylaxie ?",
                       "Stylo d'adrénaline disponible ?"],
    },

    # ---- PÉDIATRIE (pertinent en consultation générale) ----
    {
        "nom": "Rougeole",
        "categorie": "infectieux",
        "symptomes": {
            "Fièvre": 0.95, "Éruption cutanée": 0.90, "Toux": 0.80,
            "Rhinorrhée": 0.70, "Rougeur oculaire": 0.65, "Fatigue": 0.60,
            "Douleurs pharyngées": 0.30, "Adénopathies": 0.35,
        },
        "red_flags": ["Encéphalite", "Pneumonie rougeoleuse"],
        "questions": ["Vacciné ROR ?", "Contage ?", "Signe de Koplik ?"],
    },
    {
        "nom": "Varicelle",
        "categorie": "infectieux",
        "symptomes": {
            "Éruption cutanée": 0.95, "Vésicules": 0.95, "Fièvre": 0.70,
            "Démangeaisons": 0.85, "Fatigue": 0.50, "Maux de tête": 0.30,
        },
        "red_flags": ["Surinfection bactérienne", "Varicelle chez adulte/immunodéprimé",
                       "Pneumopathie varicelleuse"],
        "questions": ["Antécédent de varicelle ?", "Contage ?", "Grossesse ?"],
    },

    # ---- GYNÉCOLOGIQUES ----
    {
        "nom": "Dysménorrhée primaire",
        "categorie": "gynécologique",
        "symptomes": {
            "Dysménorrhée": 0.95, "Douleurs pelviennes": 0.85, "Nausées": 0.40,
            "Vomissements": 0.25, "Diarrhée": 0.30, "Maux de tête": 0.35,
            "Fatigue": 0.40, "Douleurs lombaires": 0.50,
        },
        "red_flags": ["Douleur résistante aux AINS", "Dyspareunie (endométriose ?)"],
        "questions": ["Depuis les premières règles ?", "Intensité (EVA) ?",
                       "Retentissement sur le quotidien ?"],
    },
    {
        "nom": "Infection génitale / Vaginite",
        "categorie": "gynécologique",
        "symptomes": {
            "Leucorrhées": 0.90, "Démangeaisons": 0.75, "Douleurs pelviennes": 0.40,
            "Brûlures mictionnelles": 0.35, "Dyspareunie": 0.30, "Rougeurs": 0.25,
        },
        "red_flags": ["Fièvre + douleur pelvienne (salpingite)"],
        "questions": ["Aspect des pertes (couleur, odeur) ?", "Rapport non protégé ?",
                       "Partenaire symptomatique ?"],
    },
]

# ============================================================
# SYNONYMES / FUZZY MATCHING — pour les symptômes tapés par le médecin
# Permet de mapper des termes libres vers les symptômes canoniques
# ============================================================

SYNONYMES = {
    # Français courant → canonique
    "fievre": "Fièvre", "fièvre": "Fièvre", "température": "Fièvre", "hyperthermie": "Hyperthermie",
    "mal de tête": "Maux de tête", "céphalée": "Maux de tête", "céphalées": "Maux de tête",
    "cephalee": "Maux de tête", "migraine": "Maux de tête",
    "toux": "Toux", "toux seche": "Toux sèche", "toux grasse": "Toux grasse",
    "toux productive": "Toux grasse", "toux non productive": "Toux sèche",
    "vomissement": "Vomissements", "vomir": "Vomissements",
    "nausee": "Nausées", "nausée": "Nausées", "envie de vomir": "Nausées",
    "diarrhee": "Diarrhée", "diarrhée": "Diarrhée", "selles liquides": "Diarrhée",
    "constipe": "Constipation", "constipé": "Constipation",
    "mal de ventre": "Douleurs abdominales", "mal au ventre": "Douleurs abdominales",
    "douleur abdominale": "Douleurs abdominales", "douleur ventre": "Douleurs abdominales",
    "mal de gorge": "Douleurs pharyngées", "angine": "Douleurs pharyngées",
    "gorge irritée": "Douleurs pharyngées", "pharyngite": "Douleurs pharyngées",
    "essoufflé": "Essoufflement", "essouffle": "Essoufflement", "souffle court": "Essoufflement",
    "du mal à respirer": "Dyspnée", "difficulté respiratoire": "Dyspnée",
    "gêne respiratoire": "Dyspnée",
    "palpitation": "Palpitations", "coeur qui bat vite": "Palpitations",
    "tachycardie": "Tachycardie", "pouls rapide": "Tachycardie",
    "bradycardie": "Bradycardie", "pouls lent": "Bradycardie",
    "vertige": "Vertiges", "tête qui tourne": "Vertiges",
    "fatigue": "Fatigue", "fatigué": "Fatigue", "épuisé": "Fatigue", "asthénie": "Asthénie",
    "insomnie": "Insomnie", "mal dormir": "Insomnie", "trouble du sommeil": "Insomnie",
    "frisson": "Frissons", "frissons": "Frissons",
    "démangeaison": "Démangeaisons", "prurit": "Démangeaisons", "ça gratte": "Démangeaisons",
    "éruption": "Éruption cutanée", "rash": "Éruption cutanée", "boutons": "Éruption cutanée",
    "rougeur": "Rougeurs", "érythème": "Rougeurs",
    "oedeme": "Œdème", "œdème": "Œdème", "gonflement": "Œdème", "enflure": "Œdème",
    "jaunisse": "Jaunisse", "ictère": "Ictère", "yeux jaunes": "Jaunisse",
    "sang dans les urines": "Sang dans les urines", "hématurie": "Hématurie",
    "sang dans les selles": "Sang dans les selles", "méléna": "Sang dans les selles",
    "mal au dos": "Douleurs lombaires", "lombalgie": "Douleurs lombaires",
    "mal aux articulations": "Douleurs articulaires", "arthralgie": "Douleurs articulaires",
    "mal aux muscles": "Douleurs musculaires", "myalgie": "Douleurs musculaires",
    "perte odorat": "Anosmie", "anosmie": "Anosmie",
    "perte goût": "Ageusie", "agueusie": "Ageusie",
    "nez bouché": "Obstruction nasale", "nez qui coule": "Rhinorrhée",
    "rhume": "Rhinorrhée", "écoulement nasal": "Rhinorrhée",
    "douleur poitrine": "Douleur thoracique", "douleur thorax": "Douleur thoracique",
    "mal de poitrine": "Douleur thoracique",
    "convulsion": "Convulsions", "crise convulsive": "Convulsions",
    "confusion": "Confusion", "confus": "Confusion", "désorienté": "Confusion",
    "syncope": "Syncope", "évanouissement": "Syncope", "perte connaissance": "Perte de conscience",
    "saignement nez": "Epistaxis", "epistaxis": "Epistaxis",
    "ganglions": "Adénopathies", "adénopathie": "Adénopathies",
    "amaigrissement": "Perte de poids", "maigrir": "Perte de poids",
    "grossir": "Prise de poids",
    "anxieux": "Anxiété", "angoisse": "Anxiété", "stress": "Anxiété",
    "déprimé": "Dépression", "triste": "Dépression",
    "brûlure urinaire": "Brûlures mictionnelles", "brulure urinaire": "Brûlures mictionnelles",
    "envie fréquente uriner": "Mictions fréquentes", "pollakiurie": "Mictions fréquentes",
    "urticaire": "Urticaire", "plaques rouges": "Urticaire",
    "sifflement": "Sifflements respiratoires", "wheezing": "Wheezing",
    "crachat sang": "Hémoptysie", "hémoptysie": "Hémoptysie",
    "dysphagie": "Dysphagie", "mal avaler": "Dysphagie",
    "trembler": "Tremblements", "tremblement": "Tremblements",
    "fourmillement": "Fourmillements", "paresthésie": "Fourmillements",
    "engourdissement": "Engourdissements", "hypoesthésie": "Engourdissements",
}

# ============================================================
# RED FLAGS GLOBAUX
# ============================================================

RED_FLAGS_GLOBAUX = [
    {"symptomes": ["Douleur thoracique", "Dyspnée", "Sueurs nocturnes"],
     "alerte": "⚠️ SYNDROME CORONARIEN AIGU — Évaluer en urgence", "priorite": "critique"},
    {"symptomes": ["Maux de tête", "Raideur de la nuque", "Fièvre"],
     "alerte": "⚠️ MÉNINGITE — PL en urgence", "priorite": "critique"},
    {"symptomes": ["Faiblesse musculaire", "Troubles de l'élocution", "Confusion"],
     "alerte": "⚠️ AVC — Appeler le 15/SAMU", "priorite": "critique"},
    {"symptomes": ["Urticaire", "Dyspnée", "Hypotension"],
     "alerte": "⚠️ CHOC ANAPHYLACTIQUE — Adrénaline IM", "priorite": "critique"},
    {"symptomes": ["Douleurs abdominales", "Fièvre", "Défense"],
     "alerte": "⚠️ ABDOMEN CHIRURGICAL — Avis chirurgical urgent", "priorite": "critique"},
    {"symptomes": ["Hémoptysie", "Dyspnée", "Tachycardie"],
     "alerte": "⚠️ EMBOLIE PULMONAIRE — Scanner en urgence", "priorite": "critique"},
    {"symptomes": ["Convulsions", "Fièvre"],
     "alerte": "⚠️ CONVULSION FÉBRILE — Évaluation neurologique", "priorite": "haute"},
    {"symptomes": ["Jaunisse", "Douleurs abdominales", "Fièvre"],
     "alerte": "⚠️ TRIADE DE CHARCOT — Angiocholite", "priorite": "haute"},
    {"symptomes": ["Perte de poids", "Sueurs nocturnes", "Fatigue"],
     "alerte": "⚠️ ALTÉRATION ÉTAT GÉNÉRAL — Bilan néoplasie", "priorite": "haute"},
]

# ============================================================
# MEDIGO V2 — AMÉLIORATIONS À IMPLÉMENTER
# Objectif: garder les IDs existants, ajouter les features manquantes,
# élargir la couverture Maroc, valider la base, vectoriser XGBoost,
# détecter les red flags avant tout diagnostic.
# Pas de synonymes Darija/Maroc ici, uniquement français médical/courant.
# ============================================================


import difflib
import json
import math
import random
import re
import unicodedata
from collections import Counter
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

MEDIGO_KB_VERSION = "2.0.0-maroc-fr"

# ------------------------------------------------------------
# 1) Extension symptômes — IMPORTANT:
# on append seulement à la fin pour ne PAS casser les index
# déjà appris par ton XGBoost.
# ------------------------------------------------------------

SYMPTOMES_V2_AJOUTS = ['Douleurs faciales',
 'Agitation',
 'Orthopnée',
 'Rougeur oculaire',
 'Larmoiement',
 'Dyspareunie',
 'Oppression thoracique',
 'Douleur thoracique constrictive',
 'Sueurs froides',
 'Irradiation bras gauche',
 'Douleur mâchoire',
 'Dyspnée au repos',
 'Expectoration mousseuse',
 'Plaie qui cicatrise mal',
 'Extrémités froides',
 'Impossibilité de parler',
 'Tirage',
 'Signes de lutte respiratoire',
 'Ronflement',
 'Pauses respiratoires nocturnes',
 'Difficulté alimentation',
 'Toux aboyante',
 'Quintes de toux',
 'Douleur épigastrique',
 'Douleur transfixiante dorsale',
 'Douleur HCD',
 'Arrêt des gaz',
 'Déshydratation',
 'Hématémèse',
 'Méléna',
 'Rectorragie',
 'Douleur fosse iliaque gauche',
 'Anémie',
 'Aphtes',
 'Douleur anale',
 'Prurit anal',
 'Douleur périnéale',
 'Rétention urinaire',
 'Jet urinaire faible',
 'Douleur pelvienne brutale',
 'Retard de règles',
 'Test grossesse positif',
 'Grossesse',
 'Douleur défécation règles',
 'Cycles irréguliers',
 'Acné',
 'Hirsutisme',
 'Douleur mammaire',
 'Masse mammaire',
 'Écoulement mamelonnaire',
 'Rétraction mamelon',
 'Saignement post-coïtal',
 'Muqueuses sèches',
 'Langue framboisée',
 'Toux chronique',
 'Ulcère cutané',
 'Croûte',
 'Ulcération génitale',
 'Écoulement urétral',
 'Douleur testiculaire',
 'Morsure animale',
 'Plaie',
 'Trismus',
 'Raideur musculaire',
 'Spasmes musculaires',
 'Prurit nocturne',
 'Cicatrices',
 'Écoulement purulent',
 'Brûlure cutanée',
 'Tache pigmentée',
 'Infections récidivantes',
 'Faim intense',
 'Ongles cassants',
 'Pica',
 'Morsure de langue',
 'Douleur neuropathique',
 'Troubles de la sensibilité',
 'Asymétrie faciale',
 'Idées suicidaires',
 'Plan suicidaire',
 'Hallucinations',
 'Délires',
 'Hypersalivation',
 'Myosis',
 'Piqûre scorpion',
 'Morsure serpent',
 'Déformation',
 'Défense abdominale',
 'Contracture abdominale',
 'Déficit moteur focal',
 'Aphasie',
 'Troubles sphinctériens',
 'Anesthésie en selle',
 'Détresse respiratoire',
 'Saturation basse']

def _extend_unique(target: List[str], values: Iterable[str]) -> None:
    seen = set(target)
    for value in values:
        if value not in seen:
            target.append(value)
            seen.add(value)

_extend_unique(SYMPTOMES_CANONIQUES, SYMPTOMES_V2_AJOUTS)

# ------------------------------------------------------------
# 2) Maladies ajoutées — couverture médecine générale + urgences
# + priorités Maroc sans synonymes marocains.
# ------------------------------------------------------------

MALADIES_V2_AJOUTS = [{'nom': 'Syndrome coronarien aigu',
  'categorie': 'cardiovasculaire',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Douleur thoracique': 0.95,
                'Oppression thoracique': 0.9,
                'Douleur thoracique constrictive': 0.85,
                'Dyspnée': 0.7,
                'Vomissements': 0.25,
                'Irradiation bras gauche': 0.65,
                'Douleur mâchoire': 0.45,
                'Palpitations': 0.35,
                'Syncope': 0.25,
                'Tachycardie': 0.4,
                'Hypotension': 0.25,
                "Sueurs froides": 0.95,
                "Essoufflement": 0.75,
                "Nausées": 0.55,
                "Anxiété": 0.45},
  'red_flags': ['Douleur thoracique au repos', 'Dyspnée', 'Syncope', 'Hypotension', 'Sueurs froides'],
  'questions': ['Heure exacte de début ?',
                'Douleur constrictive rétrosternale ?',
                'Irradiation bras/mâchoire/dos ?',
                'Facteurs de risque cardiovasculaire ?',
                "Prise d'aspirine ou anticoagulant ?"]},
 {'nom': 'Infarctus du myocarde',
  'categorie': 'cardiovasculaire',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Douleur thoracique': 0.95,
                'Oppression thoracique': 0.9,
                'Dyspnée': 0.7,
                'Nausées': 0.55,
                'Vomissements': 0.35,
                'Irradiation bras gauche': 0.7,
                'Douleur mâchoire': 0.5,
                'Malaise': 0.55,
                'Syncope': 0.2,
                'Tachycardie': 0.45,
                'Hypotension': 0.3,
                "Sueurs froides": 0.95,
                "Essoufflement": 0.75,
                "Anxiété": 0.45},
  'red_flags': ['URGENCE VITALE', 'Douleur > 20 min', 'Troubles hémodynamiques'],
  'questions': ['Douleur depuis combien de minutes ?',
                'Antécédent coronarien ?',
                'Diabète/HTA/tabac ?',
                'ECG disponible ?']},
 {'nom': 'Fibrillation auriculaire',
  'categorie': 'cardiovasculaire',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Palpitations': 0.9,
                'Tachycardie': 0.8,
                'Dyspnée': 0.45,
                'Fatigue': 0.45,
                'Étourdissements': 0.35,
                'Syncope': 0.2,
                'Douleur thoracique': 0.25,
                'Anxiété': 0.3},
  'red_flags': ['Douleur thoracique', 'Syncope', 'Déficit neurologique', 'Hypotension'],
  'questions': ['Début brutal ?',
                'Pouls irrégulier ?',
                'Antécédent FA ?',
                'Traitement anticoagulant ?',
                'Hyperthyroïdie connue ?']},
 {'nom': 'Œdème aigu du poumon',
  'categorie': 'cardiovasculaire',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Dyspnée': 0.98,
                'Dyspnée au repos': 0.9,
                'Orthopnée': 0.85,
                'Toux sèche': 0.55,
                'Expectoration mousseuse': 0.6,
                'Hypoxie': 0.8,
                'Tachypnée': 0.8,
                'Tachycardie': 0.7,
                'Cyanose': 0.45,
                'Œdème des membres inférieurs': 0.5,
                'Anxiété': 0.55},
  'red_flags': ['SpO2 basse', 'Détresse respiratoire', 'Cyanose', 'Confusion'],
  'questions': ['Insuffisance cardiaque connue ?',
                'Dyspnée en position couchée ?',
                'Prise de poids rapide ?',
                'HTA très élevée ?']},
 {'nom': 'Péricardite aiguë',
  'categorie': 'cardiovasculaire',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Douleur thoracique': 0.9,
                'Douleur pleurale': 0.6,
                'Fièvre': 0.45,
                'Fatigue': 0.55,
                'Dyspnée': 0.35,
                'Palpitations': 0.25,
                'Douleur thoracique constrictive': 0.35},
  'red_flags': ['Tamponnade', 'Hypotension', 'Syncope', 'Dyspnée sévère'],
  'questions': ['Douleur soulagée penché en avant ?',
                "Aggravée à l'inspiration ?",
                'Infection virale récente ?',
                'Antécédent tuberculose ?']},
 {'nom': 'Myocardite',
  'categorie': 'cardiovasculaire',
  'priorite_maroc': 'moyenne',
  'urgence': True,
  'symptomes': {'Douleur thoracique': 0.65,
                'Dyspnée': 0.65,
                'Palpitations': 0.6,
                'Fatigue': 0.75,
                'Fièvre': 0.45,
                'Tachycardie': 0.55,
                'Syncope': 0.25,
                'Malaise': 0.55},
  'red_flags': ['Syncope', 'Troubles du rythme', 'Insuffisance cardiaque aiguë'],
  'questions': ['Syndrome viral récent ?', 'Douleur thoracique ?', 'Palpitations ?', 'Sport intense récent ?']},
 {'nom': 'Crise hypertensive',
  'categorie': 'cardiovasculaire',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Hypertension': 0.98,
                'Maux de tête': 0.7,
                'Troubles de la vision': 0.55,
                'Douleur thoracique': 0.35,
                'Dyspnée': 0.35,
                'Nausées': 0.3,
                'Confusion': 0.2,
                'Epistaxis': 0.25,
                'Acouphènes': 0.25},
  'red_flags': ['Déficit neurologique', 'Douleur thoracique', 'Dyspnée', 'Confusion', 'TA très élevée'],
  'questions': ['Valeur tensionnelle exacte ?',
                'Mesurée au repos ?',
                'Traitement oublié ?',
                'Signes neurologiques ou thoraciques ?']},
 {'nom': 'Artériopathie oblitérante des membres inférieurs',
  'categorie': 'cardiovasculaire',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Claudication intermittente': 0.9,
                "Douleur à l'effort": 0.75,
                'Douleur au repos': 0.4,
                'Pâleur': 0.35,
                'Fourmillements': 0.3,
                'Engourdissements': 0.3,
                'Plaie qui cicatrise mal': 0.45,
                'Extrémités froides': 0.45},
  'red_flags': ['Douleur de repos', 'Ischémie aiguë', 'Pied froid et pâle'],
  'questions': ['Distance de marche ?', 'Tabagisme ?', 'Diabète ?', 'Plaie du pied ?']},
 {'nom': 'Syncope vaso-vagale',
  'categorie': 'cardiovasculaire',
  'priorite_maroc': 'basse',
  'urgence': False,
  'symptomes': {'Syncope': 0.9,
                'Lipothymie': 0.85,
                'Nausées': 0.45,
                'Sueurs froides': 0.55,
                'Pâleur': 0.55,
                'Étourdissements': 0.6,
                'Fatigue': 0.35},
  'red_flags': ["Syncope à l'effort", 'Douleur thoracique', 'Palpitations', 'Antécédent cardiaque'],
  'questions': ['Prodromes présents ?',
                'Déclenchée par douleur/chaleur/station debout ?',
                'Traumatisme ?',
                'Récupération rapide ?']},
 {'nom': 'Asthme aigu grave',
  'categorie': 'respiratoire',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Dyspnée': 0.98,
                'Sifflements respiratoires': 0.9,
                'Wheezing': 0.85,
                'Impossibilité de parler': 0.85,
                'Tirage': 0.7,
                'Signes de lutte respiratoire': 0.75,
                'Cyanose': 0.45,
                'Hypoxie': 0.65,
                'Tachypnée': 0.75,
                'Tachycardie': 0.65,
                'Anxiété': 0.6,
                'Toux sèche': 0.55},
  'red_flags': ['Impossibilité de parler', 'Cyanose', 'SpO2 basse', 'Silence auscultatoire'],
  'questions': ['DEP si disponible ?',
                'Inhalateur utilisé combien de fois ?',
                'Hospitalisation antérieure ?',
                'Facteur déclenchant ?']},
 {'nom': 'Pneumothorax',
  'categorie': 'respiratoire',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Douleur thoracique': 0.85,
                'Douleur pleurale': 0.8,
                'Dyspnée': 0.8,
                'Toux sèche': 0.3,
                'Tachycardie': 0.45,
                'Hypoxie': 0.35,
                'Cyanose': 0.2,
                'Malaise': 0.25},
  'red_flags': ['Détresse respiratoire', 'Hypotension', 'Cyanose', 'Pneumothorax compressif'],
  'questions': ['Début brutal ?', 'Traumatisme thoracique ?', 'Grand jeune fumeur ?', 'Douleur unilatérale ?']},
 {'nom': 'Pleurésie',
  'categorie': 'respiratoire',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Douleur pleurale': 0.9,
                'Dyspnée': 0.6,
                'Toux sèche': 0.45,
                'Fièvre': 0.45,
                'Douleur thoracique': 0.65,
                'Fatigue': 0.4,
                'Sueurs nocturnes': 0.25},
  'red_flags': ['Dyspnée sévère', 'Hypoxie', 'Suspicion embolie pulmonaire ou tuberculose'],
  'questions': ["Douleur à l'inspiration ?", 'Fièvre ?', 'Contexte tuberculose/cancer ?', 'Traumatisme ?']},
 {'nom': 'Apnée obstructive du sommeil',
  'categorie': 'respiratoire',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Somnolence excessive': 0.9,
                'Ronflement': 0.85,
                'Pauses respiratoires nocturnes': 0.8,
                'Maux de tête': 0.45,
                'Fatigue': 0.7,
                'Hypertension': 0.35,
                'Insomnie': 0.25},
  'red_flags': ['Somnolence au volant', 'HTA sévère', 'Insuffisance respiratoire'],
  'questions': ['Ronflement fort ?', 'Pauses respiratoires observées ?', 'Somnolence diurne ?', 'IMC élevé ?']},
 {'nom': 'Bronchiolite',
  'categorie': 'pédiatrie',
  'priorite_maroc': 'haute',
  'urgence': False,
  'symptomes': {'Toux': 0.9,
                'Sifflements respiratoires': 0.75,
                'Wheezing': 0.75,
                'Dyspnée': 0.6,
                'Tachypnée': 0.65,
                'Fièvre': 0.35,
                'Rhinorrhée': 0.7,
                'Tirage': 0.55,
                'Difficulté alimentation': 0.6,
                'Hypoxie': 0.3},
  'red_flags': ['Âge < 3 mois', 'Tirage important', 'Apnées', 'Difficulté alimentation', 'Hypoxie'],
  'questions': ['Âge ?', 'Boit moins de la moitié ?', 'Apnées ?', 'Prématurité ?']},
 {'nom': 'Laryngite aiguë',
  'categorie': 'pédiatrie',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Toux aboyante': 0.9,
                'Enrouement': 0.75,
                'Stridor': 0.7,
                'Fièvre': 0.45,
                'Dyspnée': 0.35,
                'Tirage': 0.35,
                'Rhinorrhée': 0.4},
  'red_flags': ['Stridor au repos', 'Cyanose', 'Tirage sévère', 'Hypoxie'],
  'questions': ['Stridor au repos ?', 'Voix rauque ?', "Âge de l'enfant ?", 'Vaccination à jour ?']},
 {'nom': 'Coqueluche',
  'categorie': 'infectieux',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Toux': 0.95,
                'Quintes de toux': 0.9,
                'Vomissements': 0.45,
                'Dyspnée': 0.3,
                'Cyanose': 0.25,
                'Fatigue': 0.5,
                'Rhinorrhée': 0.4,
                'Fièvre': 0.2},
  'red_flags': ['Nourrisson', 'Apnées', 'Cyanose', 'Déshydratation'],
  'questions': ['Toux par quintes ?', 'Chant du coq ?', 'Vaccination ?', 'Contact nourrisson/femme enceinte ?']},
 {'nom': 'Cancer bronchique suspect',
  'categorie': 'respiratoire',
  'priorite_maroc': 'haute',
  'urgence': False,
  'symptomes': {'Toux': 0.75,
                'Hémoptysie': 0.6,
                'Perte de poids': 0.65,
                'Fatigue': 0.6,
                'Dyspnée': 0.45,
                'Douleur thoracique': 0.4,
                'Sueurs nocturnes': 0.25,
                "Perte d'appétit": 0.45},
  'red_flags': ['Hémoptysie', 'Altération état général', 'Douleur thoracique persistante'],
  'questions': ['Tabagisme ?', 'Durée de la toux ?', 'Hémoptysie ?', 'Perte de poids chiffrée ?']},
 {'nom': 'Pancréatite aiguë',
  'categorie': 'digestif',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Douleurs abdominales': 0.75,
                'Douleur épigastrique': 0.95,
                'Douleur transfixiante dorsale': 0.85,
                'Nausées': 0.70,
                'Vomissements': 0.65,
                'Fièvre': 0.25,
                'Tachycardie': 0.45,
                'Ballonnements': 0.35,
                'Malaise': 0.35},
  'red_flags': ['Choc', 'Défaillance respiratoire', 'Douleur intense persistante'],
  'questions': ['Douleur irradiant dans le dos ?', 'Calculs biliaires ?', 'Alcool ?', 'Vomissements incoercibles ?']},
 {'nom': 'Angiocholite',
  'categorie': 'digestif',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Fièvre': 0.9,
                'Frissons': 0.75,
                'Jaunisse': 0.8,
                'Ictère': 0.8,
                'Douleur HCD': 0.85,
                'Douleurs abdominales': 0.8,
                'Nausées': 0.45,
                'Vomissements': 0.35,
                'Confusion': 0.25,
                'Hypotension': 0.2},
  'red_flags': ['Triade de Charcot', 'Confusion', 'Hypotension', 'Sepsis'],
  'questions': ['Douleur hypochondre droit ?', 'Ictère ?', 'Frissons ?', 'Antécédent calculs biliaires ?']},
 {'nom': 'Occlusion intestinale',
  'categorie': 'digestif',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Douleurs abdominales': 0.9,
                'Vomissements': 0.8,
                'Ballonnements': 0.85,
                'Constipation': 0.7,
                'Arrêt des gaz': 0.9,
                'Nausées': 0.6,
                'Tachycardie': 0.35,
                'Déshydratation': 0.4},
  'red_flags': ['Défense abdominale', 'Fièvre', 'Choc', 'Vomissements fécaloïdes'],
  'questions': ['Arrêt des gaz ?', 'Vomissements ?', 'Chirurgie abdominale antérieure ?', 'Hernie connue ?']},
 {'nom': 'Hémorragie digestive haute',
  'categorie': 'digestif',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Hématémèse': 0.9,
                'Méléna': 0.85,
                'Sang dans les selles': 0.55,
                'Pâleur': 0.65,
                'Fatigue': 0.55,
                'Syncope': 0.35,
                'Tachycardie': 0.55,
                'Hypotension': 0.45,
                'Douleurs abdominales': 0.35},
  'red_flags': ['Hématémèse abondante', 'Méléna', 'Syncope', 'Hypotension'],
  'questions': ['Quantité de sang ?', 'Prise AINS/aspirine/anticoagulant ?', 'Cirrhose connue ?', 'Méléna ?']},
 {'nom': 'Hémorragie digestive basse',
  'categorie': 'digestif',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Sang dans les selles': 0.9,
                'Rectorragie': 0.9,
                'Douleurs abdominales': 0.35,
                'Diarrhée': 0.3,
                'Pâleur': 0.45,
                'Fatigue': 0.45,
                'Tachycardie': 0.35,
                'Hypotension': 0.25},
  'red_flags': ['Saignement abondant', 'Malaise', 'Hypotension', 'Anticoagulants'],
  'questions': ['Sang rouge ou noir ?', 'Quantité ?', 'Douleur ?', 'Anticoagulants ?', 'Âge > 50 ans ?']},
 {'nom': 'Diverticulite aiguë',
  'categorie': 'digestif',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Douleurs abdominales': 0.85,
                'Douleur fosse iliaque gauche': 0.8,
                'Fièvre': 0.6,
                'Constipation': 0.4,
                'Diarrhée': 0.35,
                'Nausées': 0.45,
                'Ballonnements': 0.35},
  'red_flags': ['Défense abdominale', 'Fièvre élevée', 'Sepsis', 'Occlusion'],
  'questions': ['Douleur FID ou FIG ?', 'Fièvre ?', 'Antécédent diverticules ?', 'Sang dans les selles ?']},
 {'nom': 'Cirrhose décompensée',
  'categorie': 'digestif',
  'priorite_maroc': 'haute',
  'urgence': False,
  'symptomes': {'Ascite': 0.8,
                'Ictère': 0.7,
                'Jaunisse': 0.7,
                'Œdème': 0.55,
                'Hématémèse': 0.35,
                'Méléna': 0.35,
                'Confusion': 0.35,
                'Fatigue': 0.65,
                'Perte de poids': 0.4,
                'Hépatomégalie': 0.4,
                'Splénomégalie': 0.35},
  'red_flags': ['Hémorragie digestive', 'Encéphalopathie', 'Fièvre avec ascite'],
  'questions': ['Hépatite B/C ?', 'Alcool ?', 'Ascite connue ?', 'Confusion ?', 'Saignement digestif ?']},
 {'nom': 'Maladie inflammatoire chronique intestinale',
  'categorie': 'digestif',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Diarrhée': 0.8,
                'Sang dans les selles': 0.55,
                'Douleurs abdominales': 0.75,
                'Perte de poids': 0.55,
                'Fatigue': 0.6,
                'Fièvre': 0.35,
                'Ténesme': 0.45,
                'Arthralgies migratrices': 0.25},
  'red_flags': ['Déshydratation', 'Sang abondant', 'Fièvre élevée', 'Amaigrissement important'],
  'questions': ['Diarrhée chronique ?', 'Sang/glaires ?', 'Symptômes nocturnes ?', 'Antécédents familiaux ?']},
 {'nom': 'Maladie cœliaque',
  'categorie': 'digestif',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Diarrhée': 0.55,
                'Selles graisseuses': 0.55,
                'Ballonnements': 0.75,
                'Douleurs abdominales': 0.55,
                'Perte de poids': 0.45,
                'Fatigue': 0.7,
                'Anémie': 0.45,
                'Aphtes': 0.25},
  'red_flags': ['Dénutrition sévère', 'Anémie sévère', 'Retard de croissance enfant'],
  'questions': ['Symptômes après gluten ?', 'Anémie ?', 'Antécédents auto-immuns ?', 'Perte de poids ?']},
 {'nom': 'Hémorroïdes',
  'categorie': 'digestif',
  'priorite_maroc': 'basse',
  'urgence': False,
  'symptomes': {'Rectorragie': 0.7,
                'Douleur anale': 0.55,
                'Prurit anal': 0.5,
                'Constipation': 0.4,
                'Sang dans les selles': 0.45},
  'red_flags': ['Saignement abondant', 'Amaigrissement', 'Âge > 50 ans', 'Anémie'],
  'questions': ['Sang rouge sur papier ?', 'Douleur ?', 'Constipation ?', 'Masse extériorisée ?']},
 {'nom': 'Fissure anale',
  'categorie': 'digestif',
  'priorite_maroc': 'basse',
  'urgence': False,
  'symptomes': {'Douleur anale': 0.9,
                'Rectorragie': 0.5,
                'Constipation': 0.45,
                'Prurit anal': 0.25,
                'Sang dans les selles': 0.35},
  'red_flags': ['Fièvre', 'Abcès', 'Immunodépression'],
  'questions': ['Douleur pendant/après selle ?', 'Constipation ?', 'Sang rouge ?', 'Traumatisme local ?']},
 {'nom': 'Toxi-infection alimentaire collective',
  'categorie': 'infectieux',
  'priorite_maroc': 'haute',
  'urgence': False,
  'symptomes': {'Diarrhée': 0.9,
                'Vomissements': 0.8,
                'Nausées': 0.8,
                'Douleurs abdominales': 0.75,
                'Crampes abdominales': 0.65,
                'Fièvre': 0.45,
                'Déshydratation': 0.4,
                'Frissons': 0.3},
  'red_flags': ['Déshydratation sévère', 'Sang dans les selles', 'Fièvre élevée', 'Sujet fragile'],
  'questions': ['Plusieurs personnes malades ?', 'Repas commun ?', 'Délai après le repas ?', 'Sang ou glaires ?']},
 {'nom': 'Prostatite aiguë',
  'categorie': 'urinaire',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Fièvre': 0.85,
                'Frissons': 0.65,
                'Brûlures mictionnelles': 0.7,
                'Mictions fréquentes': 0.65,
                'Douleurs pelviennes': 0.55,
                'Douleur périnéale': 0.75,
                'Rétention urinaire': 0.35,
                'Fatigue': 0.55,
                'Douleurs lombaires': 0.35},
  'red_flags': ['Sepsis', "Rétention aiguë d'urine", 'Immunodépression'],
  'questions': ['Homme ?', 'Douleur périnéale ?', 'Fièvre ?', 'Rétention urinaire ?']},
 {'nom': "Rétention aiguë d'urine",
  'categorie': 'urinaire',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Rétention urinaire': 0.95,
                'Douleurs pelviennes': 0.8,
                'Douleurs abdominales': 0.5,
                'Mictions fréquentes': 0.3,
                'Agitation': 0.35,
                'Anxiété': 0.3},
  'red_flags': ['Globe vésical douloureux', 'Insuffisance rénale', 'Fièvre'],
  'questions': ["Impossible d'uriner depuis quand ?",
                'HBP connue ?',
                'Médicaments anticholinergiques ?',
                'Douleur importante ?']},
 {'nom': 'Colique néphrétique fébrile',
  'categorie': 'urinaire',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Douleurs lombaires': 0.95,
                'Fièvre': 0.85,
                'Frissons': 0.7,
                'Nausées': 0.65,
                'Vomissements': 0.55,
                'Hématurie': 0.45,
                'Sang dans les urines': 0.45,
                'Tachycardie': 0.45,
                'Agitation': 0.55},
  'red_flags': ['Obstacle infecté', 'Sepsis', 'Anurie', 'Rein unique'],
  'questions': ['Fièvre mesurée ?', 'Douleur latéralisée ?', 'Antécédent calcul ?', 'Urines présentes ?']},
 {'nom': 'Insuffisance rénale aiguë',
  'categorie': 'néphrologie',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Oligurie': 0.75,
                'Œdème': 0.45,
                'Fatigue': 0.55,
                'Nausées': 0.4,
                'Vomissements': 0.35,
                'Dyspnée': 0.3,
                'Confusion': 0.2,
                'Hypertension': 0.35,
                'Douleurs lombaires': 0.25},
  'red_flags': ['Anurie', 'Hyperkaliémie suspectée', 'Confusion', 'OAP'],
  'questions': ['Baisse des urines ?',
                'Déshydratation ?',
                'Médicaments AINS/IEC/diurétiques ?',
                'Créatinine récente ?']},
 {'nom': 'Insuffisance rénale chronique',
  'categorie': 'néphrologie',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Fatigue': 0.7,
                'Œdème': 0.45,
                'Hypertension': 0.55,
                'Prurit généralisé': 0.35,
                'Nausées': 0.25,
                'Oligurie': 0.2,
                'Pâleur': 0.35,
                'Dyspnée': 0.25},
  'red_flags': ['Dyspnée/OAP', 'Confusion', 'Hyperkaliémie suspectée', 'Oligurie sévère'],
  'questions': ['Diabète/HTA ?', 'Créatinine connue ?', 'Œdèmes ?', 'Urines mousseuses ?']},
 {'nom': 'Hyperplasie bénigne de la prostate',
  'categorie': 'urinaire',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Nycturie': 0.8,
                'Mictions fréquentes': 0.7,
                'Jet urinaire faible': 0.8,
                'Rétention urinaire': 0.35,
                'Brûlures mictionnelles': 0.2,
                'Incontinence urinaire': 0.25},
  'red_flags': ['Rétention aiguë', 'Hématurie', 'Fièvre', 'Insuffisance rénale'],
  'questions': ['Âge ?', 'Jet faible ?', 'Levers nocturnes ?', 'Sensation de vidange incomplète ?']},
 {'nom': 'Grossesse extra-utérine',
  'categorie': 'gynécologique',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Douleurs pelviennes': 0.9,
                'Douleur pelvienne brutale': 0.8,
                'Saignements vaginaux': 0.75,
                'Aménorrhée': 0.7,
                'Retard de règles': 0.8,
                'Test grossesse positif': 0.85,
                'Syncope': 0.3,
                'Hypotension': 0.25,
                'Douleurs abdominales': 0.5},
  'red_flags': ['Syncope', 'Hypotension', 'Douleur brutale', 'Test grossesse positif'],
  'questions': ['Date des dernières règles ?',
                'Test grossesse ?',
                'Saignements ?',
                'Douleur latéralisée ?',
                'Malaise/syncope ?']},
 {'nom': 'Fausse couche spontanée',
  'categorie': 'gynécologique',
  'priorite_maroc': 'haute',
  'urgence': False,
  'symptomes': {'Saignements vaginaux': 0.9,
                'Douleurs pelviennes': 0.75,
                'Douleurs abdominales': 0.4,
                'Test grossesse positif': 0.8,
                'Retard de règles': 0.7,
                'Malaise': 0.25},
  'red_flags': ['Saignement abondant', 'Fièvre', 'Malaise', 'Douleur intense'],
  'questions': ['Âge gestationnel ?', 'Quantité de sang ?', 'Fièvre ?', 'Douleur unilatérale ?']},
 {'nom': 'Prééclampsie',
  'categorie': 'gynécologique',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Grossesse': 0.9,
                'Hypertension': 0.9,
                'Maux de tête': 0.7,
                'Troubles de la vision': 0.65,
                'Douleur HCD': 0.45,
                'Œdème': 0.45,
                'Nausées': 0.3,
                'Vomissements': 0.25,
                'Oligurie': 0.25},
  'red_flags': ['TA élevée grossesse', 'Troubles visuels', 'Céphalée intense', 'Douleur HCD', 'Oligurie'],
  'questions': ['Terme de grossesse ?', 'Valeur TA ?', 'Protéinurie ?', 'Céphalées/troubles visuels ?']},
 {'nom': 'Éclampsie',
  'categorie': 'gynécologique',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Grossesse': 0.9,
                'Convulsions': 0.95,
                'Hypertension': 0.8,
                'Maux de tête': 0.6,
                'Troubles de la vision': 0.55,
                'Confusion': 0.45,
                'Œdème': 0.3},
  'red_flags': ['URGENCE VITALE', 'Convulsions pendant grossesse/post-partum'],
  'questions': ['Grossesse ou post-partum ?', 'TA ?', 'Céphalées avant crise ?', 'Antécédent prééclampsie ?']},
 {'nom': 'Salpingite / infection pelvienne',
  'categorie': 'gynécologique',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Douleurs pelviennes': 0.85,
                'Fièvre': 0.6,
                'Leucorrhées': 0.65,
                'Dyspareunie': 0.55,
                'Saignements vaginaux': 0.35,
                'Brûlures mictionnelles': 0.3,
                'Douleurs abdominales': 0.45},
  'red_flags': ['Grossesse', 'Douleur intense', 'Fièvre élevée', 'Abcès tubo-ovarien'],
  'questions': ['Rapport non protégé ?',
                'Pertes malodorantes ?',
                'Douleur mobilisation utérine ?',
                'Test grossesse ?']},
 {'nom': 'Endométriose',
  'categorie': 'gynécologique',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Dysménorrhée': 0.85,
                'Douleurs pelviennes': 0.75,
                'Dyspareunie': 0.65,
                'Douleurs lombaires': 0.35,
                'Douleur défécation règles': 0.45,
                'Fatigue': 0.4,
                'Saignements vaginaux': 0.25},
  'red_flags': ['Douleur aiguë inhabituelle', 'Grossesse extra-utérine à éliminer'],
  'questions': ['Douleurs pendant règles ?',
                'Dyspareunie profonde ?',
                'Infertilité ?',
                'Douleur à la défécation pendant règles ?']},
 {'nom': 'Syndrome des ovaires polykystiques',
  'categorie': 'gynécologique',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Aménorrhée': 0.7,
                'Cycles irréguliers': 0.85,
                'Prise de poids': 0.45,
                'Acné': 0.55,
                'Hirsutisme': 0.7,
                'Alopécie': 0.25},
  'red_flags': ['Saignements abondants', 'Douleur pelvienne aiguë', 'Grossesse'],
  'questions': ['Cycles irréguliers ?', 'Hirsutisme/acné ?', 'Prise de poids ?', 'Désir de grossesse ?']},
 {'nom': 'Mastite',
  'categorie': 'gynécologique',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Douleur mammaire': 0.85,
                'Rougeurs': 0.7,
                'Fièvre': 0.65,
                'Fatigue': 0.45,
                'Frissons': 0.4,
                'Œdème': 0.3},
  'red_flags': ['Abcès', 'Sepsis', 'Immunodépression'],
  'questions': ['Allaitement ?', 'Zone rouge douloureuse ?', 'Fièvre ?', 'Écoulement mamelonnaire ?']},
 {'nom': 'Cancer du sein suspect',
  'categorie': 'gynécologique',
  'priorite_maroc': 'haute',
  'urgence': False,
  'symptomes': {'Masse mammaire': 0.9,
                'Douleur mammaire': 0.25,
                'Écoulement mamelonnaire': 0.4,
                'Rétraction mamelon': 0.55,
                'Adénopathies': 0.45,
                'Perte de poids': 0.25,
                'Fatigue': 0.25},
  'red_flags': ['Masse dure fixe', "Peau d'orange", 'Écoulement sanglant', 'Adénopathie axillaire'],
  'questions': ['Masse palpable ?', 'Depuis quand ?', 'Antécédent familial ?', 'Écoulement ou rétraction ?']},
 {'nom': "Cancer du col de l'utérus suspect",
  'categorie': 'gynécologique',
  'priorite_maroc': 'haute',
  'urgence': False,
  'symptomes': {'Saignements vaginaux': 0.7,
                'Saignement post-coïtal': 0.75,
                'Leucorrhées': 0.55,
                'Douleurs pelviennes': 0.35,
                'Dyspareunie': 0.35,
                'Perte de poids': 0.3},
  'red_flags': ['Saignement post-coïtal', 'Leucorrhées fétides', 'Douleurs pelviennes persistantes'],
  'questions': ['Dernier frottis/HPV ?',
                'Saignements après rapport ?',
                'Vaccination HPV ?',
                'Leucorrhées malodorantes ?']},
 {'nom': "Déshydratation aiguë de l'enfant",
  'categorie': 'pédiatrie',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Déshydratation': 0.9,
                'Diarrhée': 0.7,
                'Vomissements': 0.7,
                'Somnolence excessive': 0.45,
                'Muqueuses sèches': 0.7,
                'Oligurie': 0.65,
                'Perte de poids': 0.35,
                'Tachycardie': 0.45,
                'Hypotension': 0.25},
  'red_flags': ['Léthargie', 'Boit impossible', 'Oligurie', 'Pli cutané persistant', 'Hypotension'],
  'questions': ['Âge ?', 'Nombre de selles/vomissements ?', 'Boit ?', 'Dernières urines ?']},
 {'nom': 'Convulsion fébrile',
  'categorie': 'pédiatrie',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Convulsions': 0.95,
                'Fièvre': 0.9,
                'Perte de conscience': 0.6,
                'Somnolence excessive': 0.35,
                'Confusion': 0.3},
  'red_flags': ['Âge < 6 mois', 'Crise > 5 minutes', 'Déficit post-critique', 'Raideur de nuque'],
  'questions': ['Durée de la crise ?', 'Âge ?', "Retour à l'état normal ?", 'Raideur de nuque ou purpura ?']},
 {'nom': 'Scarlatine',
  'categorie': 'infectieux',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Fièvre': 0.85,
                'Douleurs pharyngées': 0.8,
                'Éruption cutanée': 0.75,
                'Langue framboisée': 0.65,
                'Adénopathies': 0.45,
                'Maux de tête': 0.35,
                'Vomissements': 0.25},
  'red_flags': ['Toxicité générale', 'Déshydratation', 'Complication ORL'],
  'questions': ['Angine associée ?', 'Éruption rugueuse ?', 'Langue framboisée ?', 'Contage scolaire ?']},
 {'nom': 'Tuberculose pulmonaire',
  'categorie': 'infectieux',
  'priorite_maroc': 'haute',
  'urgence': False,
  'symptomes': {'Toux chronique': 0.9,
                'Toux': 0.85,
                'Hémoptysie': 0.45,
                'Sueurs nocturnes': 0.8,
                'Perte de poids': 0.75,
                'Fièvre': 0.65,
                'Fatigue': 0.8,
                "Perte d'appétit": 0.6,
                'Dyspnée': 0.35,
                'Douleur thoracique': 0.3,
                'Adénopathies': 0.25},
  'red_flags': ['Hémoptysie abondante', 'Dyspnée sévère', 'Méningite tuberculeuse suspectée'],
  'questions': ['Toux > 2 semaines ?',
                'Contact tuberculeux ?',
                'Perte de poids ?',
                'Sueurs nocturnes ?',
                'VIH/immunodépression ?']},
 {'nom': 'Tuberculose ganglionnaire',
  'categorie': 'infectieux',
  'priorite_maroc': 'haute',
  'urgence': False,
  'symptomes': {'Adénopathies': 0.9,
                'Fièvre': 0.45,
                'Sueurs nocturnes': 0.65,
                'Perte de poids': 0.6,
                'Fatigue': 0.65,
                "Perte d'appétit": 0.4,
                'Toux': 0.2},
  'red_flags': ['Compression', 'Fistulisation', 'Altération état général sévère'],
  'questions': ['Ganglion cervical ?', 'Depuis combien de semaines ?', 'Contage TB ?', 'Signes respiratoires ?']},
 {'nom': 'Tuberculose pleurale',
  'categorie': 'infectieux',
  'priorite_maroc': 'haute',
  'urgence': False,
  'symptomes': {'Douleur pleurale': 0.75,
                'Dyspnée': 0.65,
                'Toux sèche': 0.55,
                'Fièvre': 0.6,
                'Sueurs nocturnes': 0.65,
                'Perte de poids': 0.55,
                'Fatigue': 0.6},
  'red_flags': ['Dyspnée sévère', 'Hypoxie', 'Altération état général'],
  'questions': ["Douleur à l'inspiration ?", 'Toux > 2 semaines ?', 'Contact TB ?', 'Radiographie/épanchement ?']},
 {'nom': 'Leishmaniose cutanée',
  'categorie': 'infectieux',
  'priorite_maroc': 'haute',
  'urgence': False,
  'symptomes': {'Lésions cutanées': 0.9,
                'Ulcère cutané': 0.85,
                'Croûte': 0.55,
                'Douleur au repos': 0.2,
                'Démangeaisons': 0.2,
                'Adénopathies': 0.25},
  'red_flags': ['Lésion visage', 'Lésions multiples', 'Immunodépression', 'Surinfection'],
  'questions': ['Voyage/résidence zone rurale ?',
                "Piqûres d'insectes ?",
                'Lésion chronique indolore ?',
                'Localisation visage ?']},
 {'nom': 'Leishmaniose viscérale',
  'categorie': 'infectieux',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Fièvre': 0.85,
                'Perte de poids': 0.75,
                'Fatigue': 0.8,
                'Splénomégalie': 0.8,
                'Hépatomégalie': 0.55,
                'Pâleur': 0.55,
                'Saignements anormaux': 0.25,
                'Adénopathies': 0.25},
  'red_flags': ['Pancytopénie suspectée', 'Fièvre prolongée', 'Altération état général'],
  'questions': ['Fièvre prolongée ?', 'Splénomégalie ?', 'Région endémique ?', 'Enfant ou immunodéprimé ?']},
 {'nom': 'Hydatidose / kyste hydatique',
  'categorie': 'infectieux',
  'priorite_maroc': 'haute',
  'urgence': False,
  'symptomes': {'Douleurs abdominales': 0.45,
                'Douleur HCD': 0.45,
                'Hépatomégalie': 0.45,
                'Toux': 0.25,
                'Dyspnée': 0.2,
                'Douleur thoracique': 0.2,
                'Urticaire': 0.15,
                'Fièvre': 0.2},
  'red_flags': ['Rupture kyste', 'Choc anaphylactique', 'Douleur aiguë', 'Ictère'],
  'questions': ['Contact chiens/ovins ?', 'Kyste hépatique connu ?', 'Douleur HCD ?', 'Toux/douleur thoracique ?']},
 {'nom': 'Brucellose',
  'categorie': 'infectieux',
  'priorite_maroc': 'haute',
  'urgence': False,
  'symptomes': {'Fièvre': 0.85,
                'Sueurs nocturnes': 0.75,
                'Fatigue': 0.8,
                'Douleurs articulaires': 0.6,
                'Douleurs musculaires': 0.55,
                'Maux de tête': 0.45,
                'Perte de poids': 0.35,
                'Douleurs lombaires': 0.3},
  'red_flags': ['Neurobrucellose', 'Endocardite', 'Grossesse'],
  'questions': ['Lait cru/fromage frais ?', 'Contact animaux ?', 'Fièvre ondulante ?', 'Douleurs articulaires ?']},
 {'nom': 'Fièvre typhoïde',
  'categorie': 'infectieux',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Fièvre': 0.9,
                'Maux de tête': 0.65,
                'Douleurs abdominales': 0.55,
                'Diarrhée': 0.45,
                'Constipation': 0.35,
                'Fatigue': 0.7,
                "Perte d'appétit": 0.55,
                'Toux sèche': 0.25,
                'Confusion': 0.2},
  'red_flags': ['Confusion', 'Hémorragie digestive', 'Perforation', 'Déshydratation'],
  'questions': ['Eau/aliments à risque ?', 'Voyage ?', 'Fièvre prolongée ?', 'Vaccination ?']},
 {'nom': 'Hépatite A',
  'categorie': 'infectieux',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Fièvre': 0.45,
                'Fatigue': 0.85,
                'Nausées': 0.7,
                'Vomissements': 0.45,
                'Jaunisse': 0.8,
                'Ictère': 0.8,
                'Urine foncée': 0.7,
                'Douleurs abdominales': 0.5,
                "Perte d'appétit": 0.75},
  'red_flags': ['Confusion', 'Saignements', 'Vomissements incoercibles', 'Grossesse'],
  'questions': ['Contage familial ?', 'Eau/aliments à risque ?', 'Ictère ?', 'Vaccination hépatite A ?']},
 {'nom': 'Hépatite B ou C chronique suspecte',
  'categorie': 'infectieux',
  'priorite_maroc': 'haute',
  'urgence': False,
  'symptomes': {'Fatigue': 0.55,
                'Ictère': 0.25,
                'Jaunisse': 0.25,
                'Douleurs abdominales': 0.25,
                "Perte d'appétit": 0.3,
                'Hépatomégalie': 0.3,
                'Ascite': 0.15},
  'red_flags': ['Ictère important', 'Ascite', 'Hémorragie digestive', 'Confusion'],
  'questions': ['Transfusion ancienne ?', 'Tatouage/piercing ?', 'Rapports non protégés ?', 'Dépistage antérieur ?']},
 {'nom': 'VIH primo-infection',
  'categorie': 'infectieux',
  'priorite_maroc': 'haute',
  'urgence': False,
  'symptomes': {'Fièvre': 0.8,
                'Fatigue': 0.75,
                'Douleurs pharyngées': 0.6,
                'Éruption cutanée': 0.55,
                'Adénopathies': 0.65,
                'Douleurs musculaires': 0.45,
                'Diarrhée': 0.3,
                'Maux de tête': 0.4},
  'red_flags': ['Méningite', 'Immunodépression sévère', 'Opportunistes'],
  'questions': ['Rapport à risque récent ?',
                'Exposition sanguine ?',
                'Dépistage VIH antérieur ?',
                "Date d'exposition ?"]},
 {'nom': 'Syphilis',
  'categorie': 'infectieux',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Ulcération génitale': 0.8,
                'Éruption cutanée': 0.45,
                'Adénopathies': 0.45,
                'Fièvre': 0.2,
                'Fatigue': 0.25,
                'Douleurs pharyngées': 0.15},
  'red_flags': ['Neurosyphilis', 'Grossesse', 'Atteinte oculaire'],
  'questions': ['Chancre indolore ?', 'Rapports non protégés ?', 'Partenaires multiples ?', 'Grossesse ?']},
 {'nom': 'Gonorrhée / urétrite',
  'categorie': 'infectieux',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Écoulement urétral': 0.95,
                'Brûlures mictionnelles': 0.70,
                'Mictions fréquentes': 0.20,
                'Douleur testiculaire': 0.25,
                'Douleurs pelviennes': 0.25,
                'Leucorrhées': 0.40},
  'red_flags': ['Douleur testiculaire aiguë', 'Fièvre', 'Salpingite', 'Grossesse'],
  'questions': ['Écoulement purulent ?',
                'Rapport non protégé ?',
                'Partenaire symptomatique ?',
                'Douleur testiculaire/pelvienne ?']},
 {'nom': 'Rage / exposition à morsure',
  'categorie': 'infectieux',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Morsure animale': 0.95, 'Plaie': 0.7, 'Anxiété': 0.3, 'Fièvre': 0.2, 'Douleur au repos': 0.25},
  'red_flags': ['Exposition rage possible',
                'Morsure chien errant',
                'Morsure visage/main',
                'Absence vaccination post-exposition'],
  'questions': ['Animal connu/vacciné ?',
                'Localisation morsure ?',
                'Date/heure morsure ?',
                'Lavage immédiat ?',
                'Vaccination antirabique ?']},
 {'nom': 'Tétanos',
  'categorie': 'infectieux',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Trismus': 0.85,
                'Raideur musculaire': 0.75,
                'Spasmes musculaires': 0.75,
                'Plaie': 0.55,
                'Fièvre': 0.25,
                'Dysphagie': 0.35,
                'Tachycardie': 0.3,
                'Sueurs froides': 0.25},
  'red_flags': ['Trismus', 'Spasmes', 'Dysautonomie', 'Vaccination inconnue'],
  'questions': ['Plaie récente ?', 'Vaccination tétanos à jour ?', 'Trismus ?', 'Spasmes douloureux ?']},
 {'nom': 'Gale',
  'categorie': 'dermatologique',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Démangeaisons': 0.95,
                'Prurit nocturne': 0.9,
                'Lésions cutanées': 0.7,
                'Éruption cutanée': 0.6,
                'Prurit généralisé': 0.75,
                'Insomnie': 0.45},
  'red_flags': ['Surinfection', 'Gale croûteuse', 'Collectivité'],
  'questions': ['Prurit nocturne ?', 'Cas dans entourage ?', 'Espaces interdigitaux ?', 'Collectivité ?']},
 {'nom': 'Teigne',
  'categorie': 'dermatologique',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Alopécie': 0.7,
                'Desquamation': 0.65,
                'Démangeaisons': 0.55,
                'Lésions cutanées': 0.65,
                'Rougeurs': 0.45,
                'Croûte': 0.35},
  'red_flags': ['Kérion', 'Surinfection', 'Épidémie scolaire'],
  'questions': ['Plaques alopéciques ?', 'Contact animaux ?', "Cas à l'école ?", 'Lésion inflammatoire ?']},
 {'nom': 'Impétigo',
  'categorie': 'dermatologique',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Lésions cutanées': 0.85,
                'Croûte': 0.8,
                'Rougeurs': 0.55,
                'Démangeaisons': 0.35,
                'Fièvre': 0.2,
                'Douleur au repos': 0.2},
  'red_flags': ['Extension rapide', 'Fièvre', 'Cellulite', 'Nourrisson'],
  'questions': ['Croûtes couleur miel ?', 'Lésions autour bouche/nez ?', 'Collectivité ?', 'Fièvre ?']},
 {'nom': 'Psoriasis',
  'categorie': 'dermatologique',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Éruption cutanée': 0.7,
                'Desquamation': 0.85,
                'Rougeurs': 0.7,
                'Démangeaisons': 0.45,
                'Lésions cutanées': 0.75,
                'Douleurs articulaires': 0.25},
  'red_flags': ['Érythrodermie', 'Arthrite sévère', 'Surinfection'],
  'questions': ['Plaques rouges squameuses ?',
                'Coudes/genoux/cuir chevelu ?',
                'Atteinte des ongles ?',
                'Douleurs articulaires ?']},
 {'nom': 'Acné',
  'categorie': 'dermatologique',
  'priorite_maroc': 'basse',
  'urgence': False,
  'symptomes': {'Acné': 0.95, 'Lésions cutanées': 0.75, 'Rougeurs': 0.4, 'Douleur au repos': 0.2, 'Cicatrices': 0.35},
  'red_flags': ['Acné fulminans', 'Fièvre', 'Douleurs articulaires'],
  'questions': ['Âge ?', 'Forme inflammatoire ?', 'Cicatrices ?', 'Traitements essayés ?']},
 {'nom': 'Érysipèle / cellulite infectieuse',
  'categorie': 'dermatologique',
  'priorite_maroc': 'haute',
  'urgence': False,
  'symptomes': {'Rougeurs': 0.85,
                'Douleur au repos': 0.7,
                'Fièvre': 0.65,
                'Œdème': 0.6,
                'Lésions cutanées': 0.55,
                'Frissons': 0.4,
                'Tachycardie': 0.35},
  'red_flags': ['Sepsis', 'Nécrose', 'Douleur disproportionnée', 'Diabète/immunodépression'],
  'questions': ['Extension rapide ?', "Porte d'entrée ?", 'Fièvre/frissons ?', 'Diabète ?']},
 {'nom': 'Abcès cutané',
  'categorie': 'dermatologique',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Lésions cutanées': 0.75,
                'Douleur au repos': 0.75,
                'Rougeurs': 0.65,
                'Œdème': 0.55,
                'Fièvre': 0.35,
                'Écoulement purulent': 0.7},
  'red_flags': ['Fièvre', 'Cellulite extensive', 'Immunodépression', 'Localisation visage'],
  'questions': ['Collection fluctuante ?', 'Écoulement pus ?', 'Diabète ?', 'Localisation ?']},
 {'nom': 'Brûlure',
  'categorie': 'traumatologie',
  'priorite_maroc': 'haute',
  'urgence': False,
  'symptomes': {'Brûlure cutanée': 0.95,
                'Douleur au repos': 0.75,
                'Rougeurs': 0.65,
                'Vésicules': 0.55,
                'Œdème': 0.4,
                'Plaie': 0.45},
  'red_flags': ['Visage/main/périnée', 'Brûlure électrique/chimique', 'Grande surface', 'Inhalation fumées'],
  'questions': ['Agent causal ?',
                'Surface approximative ?',
                'Localisation ?',
                'Inhalation fumées ?',
                'Vaccin tétanos ?']},
 {'nom': 'Mélanome suspect',
  'categorie': 'dermatologique',
  'priorite_maroc': 'haute',
  'urgence': False,
  'symptomes': {'Lésions cutanées': 0.8,
                'Tache pigmentée': 0.85,
                'Saignements anormaux': 0.25,
                'Démangeaisons': 0.25,
                'Douleur au repos': 0.15},
  'red_flags': ['ABCDE positif', 'Lésion évolutive', 'Saignement', 'Ulcération'],
  'questions': ['Asymétrie ?',
                'Bords irréguliers ?',
                'Couleurs multiples ?',
                'Diamètre > 6 mm ?',
                'Évolution récente ?']},
 {'nom': 'Diabète type 2 suspect',
  'categorie': 'endocrinien',
  'priorite_maroc': 'haute',
  'urgence': False,
  'symptomes': {'Polydipsie': 0.7,
                'Polyurie': 0.7,
                'Fatigue': 0.6,
                'Troubles de la vision': 0.35,
                'Mictions fréquentes': 0.55,
                'Prise de poids': 0.3,
                'Perte de poids': 0.25,
                'Infections récidivantes': 0.35},
  'red_flags': ['Acidocétose', 'Syndrome hyperosmolaire', 'Altération conscience'],
  'questions': ['Glycémie capillaire ?', 'Antécédents familiaux ?', 'IMC ?', 'Diabète gestationnel antérieur ?']},
 {'nom': 'Hypoglycémie',
  'categorie': 'endocrinien',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Sueurs froides': 0.8,
                'Tremblements': 0.75,
                'Palpitations': 0.6,
                'Faim intense': 0.65,
                'Confusion': 0.6,
                'Malaise': 0.7,
                'Convulsions': 0.25,
                'Perte de conscience': 0.25,
                'Anxiété': 0.4},
  'red_flags': ['Confusion', 'Convulsions', 'Perte de conscience', 'Diabétique sous insuline/sulfamide'],
  'questions': ['Glycémie capillaire ?', 'Diabète traité ?', 'Dernier repas ?', 'Insuline/sulfamide ?']},
 {'nom': 'Acidocétose diabétique',
  'categorie': 'endocrinien',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Polydipsie': 0.75,
                'Polyurie': 0.7,
                'Nausées': 0.65,
                'Vomissements': 0.55,
                'Douleurs abdominales': 0.55,
                'Déshydratation': 0.7,
                'Tachypnée': 0.65,
                'Confusion': 0.3,
                'Fatigue': 0.7,
                'Perte de poids': 0.45},
  'red_flags': ['Polypnée/Kussmaul', 'Vomissements', 'Déshydratation', 'Confusion'],
  'questions': ['Diabète type 1 ?', 'Glycémie/cétones ?', 'Infection déclenchante ?', 'Oubli insuline ?']},
 {'nom': 'Syndrome hyperosmolaire diabétique',
  'categorie': 'endocrinien',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Soif excessive': 0.8,
                'Polyurie': 0.75,
                'Déshydratation': 0.85,
                'Confusion': 0.6,
                'Somnolence excessive': 0.55,
                'Fatigue': 0.65,
                'Malaise': 0.5,
                'Hypotension': 0.25,
                'Tachycardie': 0.45},
  'red_flags': ['Confusion', 'Déshydratation sévère', 'Sujet âgé', 'Hypotension'],
  'questions': ['Glycémie très élevée ?', 'Sujet âgé diabétique ?', 'Fièvre/infection ?', 'Baisse des apports ?']},
 {'nom': 'Carence martiale / anémie ferriprive',
  'categorie': 'hématologique',
  'priorite_maroc': 'haute',
  'urgence': False,
  'symptomes': {'Fatigue': 0.85,
                'Pâleur': 0.7,
                'Essoufflement': 0.45,
                'Palpitations': 0.35,
                'Vertiges': 0.35,
                'Maux de tête': 0.3,
                'Ongles cassants': 0.3,
                'Pica': 0.25},
  'red_flags': ['Anémie sévère', 'Saignement actif', 'Grossesse', 'Méléna/rectorragie'],
  'questions': ['Règles abondantes ?', 'Saignement digestif ?', 'Grossesse ?', 'Régime pauvre en fer ?']},
 {'nom': 'Carence en vitamine D',
  'categorie': 'endocrinien',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Fatigue': 0.5,
                'Douleurs musculaires': 0.5,
                'Douleurs osseuses': 0.55,
                'Faiblesse musculaire': 0.4,
                'Crampes musculaires': 0.3},
  'red_flags': ['Douleurs osseuses sévères', 'Fractures', 'Faiblesse majeure'],
  'questions': ['Exposition solaire ?', 'Grossesse/allaitement ?', 'Douleurs osseuses ?', 'Supplémentation ?']},
 {'nom': 'Épilepsie / crise convulsive',
  'categorie': 'neurologique',
  'priorite_maroc': 'haute',
  'urgence': False,
  'symptomes': {'Convulsions': 0.9,
                'Perte de conscience': 0.65,
                'Confusion': 0.45,
                'Morsure de langue': 0.55,
                'Incontinence urinaire': 0.3,
                'Somnolence excessive': 0.35,
                'Maux de tête': 0.25},
  'red_flags': ['Crise > 5 minutes', 'Crises répétées', 'Traumatisme', 'Grossesse', 'Fièvre + raideur nuque'],
  'questions': ['Première crise ?',
                'Durée ?',
                "Retour à l'état normal ?",
                'Traitement antiépileptique ?',
                'Facteur déclenchant ?']},
 {'nom': 'Encéphalite',
  'categorie': 'neurologique',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Fièvre': 0.8,
                'Confusion': 0.8,
                'Maux de tête': 0.7,
                'Convulsions': 0.45,
                'Troubles de la mémoire': 0.35,
                'Somnolence excessive': 0.55,
                'Raideur de la nuque': 0.35,
                'Vomissements': 0.35},
  'red_flags': ['Troubles de conscience', 'Convulsions', 'Déficit neurologique', 'Fièvre'],
  'questions': ['Confusion récente ?', 'Fièvre ?', 'Convulsions ?', 'Voyage/morsure ?']},
 {'nom': 'Neuropathie diabétique',
  'categorie': 'neurologique',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Fourmillements': 0.75,
                'Engourdissements': 0.7,
                'Douleur neuropathique': 0.75,
                'Douleur au repos': 0.45,
                'Faiblesse musculaire': 0.25,
                'Troubles de la sensibilité': 0.6},
  'red_flags': ['Plaie du pied', 'Déficit moteur', 'Douleur aiguë asymétrique'],
  'questions': ['Diabète connu ?', 'Symptômes en chaussettes ?', 'Plaies aux pieds ?', 'Contrôle glycémique ?']},
 {'nom': 'Paralysie faciale périphérique',
  'categorie': 'neurologique',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Asymétrie faciale': 0.9,
                'Faiblesse musculaire': 0.45,
                'Douleurs auriculaires': 0.25,
                'Troubles de la vision': 0.25,
                'Larmoiement': 0.35,
                'Engourdissements': 0.2},
  'red_flags': ['Signes AVC', 'Déficit membre', 'Troubles élocution', 'Atteinte bilatérale'],
  'questions': ['Front atteint ?',
                'Début brutal ?',
                'Troubles de parole ou faiblesse bras ?',
                'Douleur oreille/zona ?']},
 {'nom': 'Attaque de panique',
  'categorie': 'psychiatrique',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Anxiété': 0.9,
                'Palpitations': 0.75,
                'Dyspnée': 0.55,
                'Douleur thoracique': 0.35,
                'Sueurs froides': 0.55,
                'Tremblements': 0.55,
                'Étourdissements': 0.45,
                'Nausées': 0.3,
                'Malaise': 0.45},
  'red_flags': ['Première douleur thoracique', 'Syncope', 'Facteurs de risque CV', 'Idées suicidaires'],
  'questions': ['Début brutal avec pic en minutes ?',
                'Peur de mourir/perdre contrôle ?',
                'Épisodes similaires ?',
                'Consommation stimulants ?']},
 {'nom': 'Risque suicidaire',
  'categorie': 'psychiatrique',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Dépression': 0.7,
                'Anxiété': 0.4,
                'Insomnie': 0.45,
                'Idées suicidaires': 0.95,
                'Plan suicidaire': 0.9,
                'Malaise': 0.35,
                'Agitation': 0.3},
  'red_flags': ['Idées suicidaires actives', 'Plan', 'Moyens disponibles', 'Isolement', 'Tentative récente'],
  'questions': ['Idées de mort ?',
                'Plan précis ?',
                'Moyens disponibles ?',
                'Tentative antérieure ?',
                'Soutien immédiat disponible ?']},
 {'nom': 'Trouble psychotique aigu',
  'categorie': 'psychiatrique',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Confusion': 0.35,
                'Agitation': 0.65,
                'Insomnie': 0.45,
                'Hallucinations': 0.85,
                'Délires': 0.85,
                'Anxiété': 0.5,
                'Irritabilité': 0.45},
  'red_flags': ['Danger pour soi/autrui', 'Agitation majeure', 'Confusion organique', 'Toxiques'],
  'questions': ['Hallucinations/délires ?', 'Risque auto/hétéro-agressif ?', 'Prise toxiques ?', 'Fièvre/confusion ?']},
 {'nom': 'Insomnie chronique',
  'categorie': 'psychiatrique',
  'priorite_maroc': 'basse',
  'urgence': False,
  'symptomes': {'Insomnie': 0.95,
                'Fatigue': 0.65,
                'Somnolence excessive': 0.45,
                'Anxiété': 0.45,
                'Dépression': 0.3,
                'Irritabilité': 0.4,
                'Troubles de la mémoire': 0.25},
  'red_flags': ['Idées suicidaires', 'Manie', 'Apnée du sommeil', 'Abus de substances'],
  'questions': ['Durée > 3 mois ?', 'Difficulté endormissement ou réveils ?', 'Caféine/écrans ?', 'Ronflement ?']},
 {'nom': 'Intoxication au monoxyde de carbone',
  'categorie': 'toxicologie',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Maux de tête': 0.85,
                'Nausées': 0.7,
                'Vomissements': 0.45,
                'Vertiges': 0.6,
                'Confusion': 0.45,
                'Perte de conscience': 0.25,
                'Fatigue': 0.65,
                'Dyspnée': 0.25},
  'red_flags': ['Plusieurs personnes symptomatiques', 'Perte de conscience', 'Grossesse', 'Troubles neurologiques'],
  'questions': ['Chauffage/chauffe-eau gaz ?',
                'Plusieurs personnes atteintes ?',
                'Lieu fermé ?',
                'Perte de connaissance ?']},
 {'nom': 'Intoxication aux organophosphorés',
  'categorie': 'toxicologie',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Hypersalivation': 0.8,
                'Larmoiement': 0.65,
                'Diarrhée': 0.6,
                'Vomissements': 0.65,
                'Dyspnée': 0.55,
                'Bradycardie': 0.45,
                'Confusion': 0.35,
                'Convulsions': 0.2,
                'Myosis': 0.7},
  'red_flags': ['Détresse respiratoire', 'Convulsions', 'Bradycardie', 'Exposition pesticide'],
  'questions': ['Exposition pesticide ?',
                'Inhalation/contact cutané/ingestion ?',
                'Délai ?',
                'Décontamination faite ?']},
 {'nom': 'Coup de chaleur',
  'categorie': 'environnemental',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Hyperthermie': 0.95,
                'Confusion': 0.7,
                'Maux de tête': 0.6,
                'Nausées': 0.45,
                'Vomissements': 0.35,
                'Tachycardie': 0.55,
                'Déshydratation': 0.6,
                'Convulsions': 0.2,
                'Perte de conscience': 0.25},
  'red_flags': ['Température très élevée', 'Confusion', 'Convulsions', 'Perte de conscience'],
  'questions': ['Exposition chaleur/effort ?', 'Température mesurée ?', 'Confusion ?', 'Hydratation ?']},
 {'nom': 'Piqûre de scorpion',
  'categorie': 'toxicologie',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Piqûre scorpion': 0.95,
                'Douleur au repos': 0.75,
                'Rougeurs': 0.35,
                'Œdème': 0.35,
                'Sueurs froides': 0.4,
                'Vomissements': 0.35,
                'Tachycardie': 0.35,
                'Hypotension': 0.2,
                'Dyspnée': 0.2},
  'red_flags': ['Enfant', 'Signes généraux', 'Vomissements répétés', 'Détresse respiratoire', 'Choc'],
  'questions': ['Âge ?', 'Heure de piqûre ?', 'Signes généraux ?', 'Localisation ?', 'Scorpion identifié ?']},
 {'nom': 'Morsure de serpent',
  'categorie': 'toxicologie',
  'priorite_maroc': 'haute',
  'urgence': True,
  'symptomes': {'Morsure serpent': 0.95,
                'Douleur au repos': 0.7,
                'Œdème': 0.65,
                'Saignements anormaux': 0.35,
                'Ecchymoses faciles': 0.35,
                'Nausées': 0.3,
                'Vomissements': 0.25,
                'Hypotension': 0.2},
  'red_flags': ['Œdème progressif', 'Saignements', 'Choc', 'Troubles neurologiques'],
  'questions': ['Heure de morsure ?',
                'Œdème progresse ?',
                'Saignements ?',
                'Garrot appliqué ?',
                'Serpent identifié ?']},
 {'nom': 'Plaie infectée',
  'categorie': 'traumatologie',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Plaie': 0.8,
                'Rougeurs': 0.65,
                'Douleur au repos': 0.55,
                'Écoulement purulent': 0.65,
                'Fièvre': 0.35,
                'Œdème': 0.45},
  'red_flags': ['Extension rapide', 'Fièvre', 'Diabète', 'Morsure', 'Corps étranger'],
  'questions': ['Date de la plaie ?', 'Vaccin tétanos ?', 'Pus ?', "Rougeur qui s'étend ?", 'Diabète ?']},
 {'nom': 'Traumatisme crânien',
  'categorie': 'traumatologie',
  'priorite_maroc': 'haute',
  'urgence': False,
  'symptomes': {'Maux de tête': 0.6,
                'Nausées': 0.35,
                'Vomissements': 0.4,
                'Perte de conscience': 0.45,
                'Confusion': 0.45,
                'Troubles de la mémoire': 0.35,
                'Vertiges': 0.35,
                'Somnolence excessive': 0.3},
  'red_flags': ['Perte de conscience', 'Vomissements répétés', 'Confusion', 'Anticoagulants', 'Déficit neurologique'],
  'questions': ['Mécanisme ?', 'Perte de connaissance ?', 'Vomissements ?', 'Anticoagulants ?', 'Âge ?']},
 {'nom': 'Fracture suspectée',
  'categorie': 'traumatologie',
  'priorite_maroc': 'moyenne',
  'urgence': False,
  'symptomes': {'Douleurs osseuses': 0.85,
                'Œdème': 0.6,
                'Ecchymoses faciles': 0.45,
                'Limitation mobilité': 0.7,
                'Déformation': 0.7,
                'Douleur au repos': 0.55},
  'red_flags': ['Fracture ouverte', 'Déficit vasculo-nerveux', 'Déformation importante', 'Douleur incontrôlable'],
  'questions': ['Traumatisme ?', 'Déformation ?', 'Appui possible ?', 'Engourdissements ou pâleur ?']}]

_existing_disease_names = {m["nom"] for m in MALADIES}
for _maladie in MALADIES_V2_AJOUTS:
    if _maladie["nom"] not in _existing_disease_names:
        MALADIES.append(_maladie)
        _existing_disease_names.add(_maladie["nom"])

# ------------------------------------------------------------
# 3) Synonymes français seulement, pas Darija.
# ------------------------------------------------------------

SYNONYMES_FR_V2 = {'oppression thoracique': 'Oppression thoracique',
 'serrement poitrine': 'Oppression thoracique',
 'douleur constrictive': 'Douleur thoracique constrictive',
 'douleur bras gauche': 'Irradiation bras gauche',
 'irradiation bras': 'Irradiation bras gauche',
 'douleur machoire': 'Douleur mâchoire',
 'sueurs froides': 'Sueurs froides',
 'orthopnee': 'Orthopnée',
 'orthopnée': 'Orthopnée',
 'essoufflement au repos': 'Dyspnée au repos',
 'dyspnee repos': 'Dyspnée au repos',
 'tirage': 'Tirage',
 'signes de lutte': 'Signes de lutte respiratoire',
 'detresse respiratoire': 'Détresse respiratoire',
 'détresse respiratoire': 'Détresse respiratoire',
 'impossible de parler': 'Impossibilité de parler',
 'toux aboyante': 'Toux aboyante',
 'quintes de toux': 'Quintes de toux',
 'ronflement': 'Ronflement',
 'pauses respiratoires': 'Pauses respiratoires nocturnes',
 'expectoration mousseuse': 'Expectoration mousseuse',
 'hematemese': 'Hématémèse',
 'hématémèse': 'Hématémèse',
 'vomir du sang': 'Hématémèse',
 'melena': 'Méléna',
 'méléna': 'Méléna',
 'selles noires': 'Méléna',
 'rectorragie': 'Rectorragie',
 'sang rouge anus': 'Rectorragie',
 'douleur epigastrique': 'Douleur épigastrique',
 'douleur hypochondre droit': 'Douleur HCD',
 'douleur hcd': 'Douleur HCD',
 'arret gaz': 'Arrêt des gaz',
 'arrêt des gaz': 'Arrêt des gaz',
 'defense abdominale': 'Défense abdominale',
 'défense abdominale': 'Défense abdominale',
 'contracture abdominale': 'Contracture abdominale',
 'douleur anale': 'Douleur anale',
 'retention urinaire': 'Rétention urinaire',
 'rétention urinaire': 'Rétention urinaire',
 'jet faible': 'Jet urinaire faible',
 'douleur testicule': 'Douleur testiculaire',
 'douleur testiculaire': 'Douleur testiculaire',
 'retard regles': 'Retard de règles',
 'retard de règles': 'Retard de règles',
 'test grossesse positif': 'Test grossesse positif',
 'enceinte': 'Grossesse',
 'grossesse': 'Grossesse',
 'douleur pendant rapports': 'Dyspareunie',
 'dyspareunie': 'Dyspareunie',
 'pertes vaginales': 'Leucorrhées',
 'saignement vaginal': 'Saignements vaginaux',
 'douleur mammaire': 'Douleur mammaire',
 'boule sein': 'Masse mammaire',
 'masse mammaire': 'Masse mammaire',
 'asymetrie faciale': 'Asymétrie faciale',
 'asymétrie faciale': 'Asymétrie faciale',
 'visage de travers': 'Asymétrie faciale',
 'aphasie': 'Aphasie',
 'difficulte parler': "Troubles de l'élocution",
 'idées suicidaires': 'Idées suicidaires',
 'idees suicidaires': 'Idées suicidaires',
 'envie de mourir': 'Idées suicidaires',
 'plan suicidaire': 'Plan suicidaire',
 'hallucinations': 'Hallucinations',
 'delires': 'Délires',
 'délires': 'Délires',
 'ulcere cutane': 'Ulcère cutané',
 'ulcère cutané': 'Ulcère cutané',
 'prurit nocturne': 'Prurit nocturne',
 'piqure scorpion': 'Piqûre scorpion',
 'piqûre scorpion': 'Piqûre scorpion',
 'morsure serpent': 'Morsure serpent',
 'morsure animale': 'Morsure animale',
 'plaie': 'Plaie',
 'pus': 'Écoulement purulent',
 'ecoulement purulent': 'Écoulement purulent',
 'écoulement purulent': 'Écoulement purulent',
 'brulure': 'Brûlure cutanée',
 'brûlure': 'Brûlure cutanée',
 'deformation': 'Déformation',
 'déformation': 'Déformation',
 'deshydratation': 'Déshydratation',
 'déshydratation': 'Déshydratation',
 'muqueuses seches': 'Muqueuses sèches',
 'myosis': 'Myosis',
 'hypersalivation': 'Hypersalivation',
 'salivation excessive': 'Hypersalivation',
 'yeux rouges': 'Rougeur oculaire',
 'rougeur oculaire': 'Rougeur oculaire',
 'larmoiement': 'Larmoiement'}
SYNONYMES.update(SYNONYMES_FR_V2)

# ------------------------------------------------------------
# 4) Red flags globaux V2.
# Ces règles passent AVANT le modèle ML.
# Format supporté:
# - symptomes: liste testée avec minimum
# - symptomes_requis: liste obligatoire en plus
# ------------------------------------------------------------

RED_FLAGS_GLOBAUX_ORIGINAL = RED_FLAGS_GLOBAUX
RED_FLAGS_GLOBAUX = [{'code': 'SCA',
  'symptomes': ['Douleur thoracique',
                'Oppression thoracique',
                'Douleur thoracique constrictive',
                'Dyspnée',
                'Sueurs froides',
                'Irradiation bras gauche',
                'Douleur mâchoire',
                'Syncope'],
  'minimum': 3,
  'alerte': '⚠️ SYNDROME CORONARIEN AIGU POSSIBLE — orientation urgence immédiate',
  'priorite': 'critique'},
 {'code': 'AVC',
  'symptomes': ['Asymétrie faciale',
                'Faiblesse musculaire',
                'Déficit moteur focal',
                "Troubles de l'élocution",
                'Aphasie',
                'Troubles de la vision',
                'Confusion'],
  'minimum': 2,
  'alerte': '⚠️ AVC/AIT POSSIBLE — début brutal = urgence immédiate',
  'priorite': 'critique'},
 {'code': 'MENINGITE',
  'symptomes': ['Maux de tête', 'Fièvre', 'Raideur de la nuque', 'Photophobie', 'Vomissements', 'Confusion', 'Purpura'],
  'minimum': 3,
  'alerte': '⚠️ MÉNINGITE POSSIBLE — avis urgent',
  'priorite': 'critique'},
 {'code': 'ANAPHYLAXIE',
  'symptomes': ['Urticaire', 'Dyspnée', 'Hypotension', 'Gonflement visage', 'Œdème', 'Wheezing', 'Syncope'],
  'minimum': 2,
  'alerte': '⚠️ ANAPHYLAXIE POSSIBLE — urgence immédiate',
  'priorite': 'critique'},
 {'code': 'ABDOMEN_CHIRURGICAL',
  'symptomes_requis': ['Douleurs abdominales'],
  'symptomes': ['Défense abdominale', 'Contracture abdominale', 'Fièvre', 'Vomissements', 'Syncope', 'Hypotension'],
  'minimum': 1,
  'alerte': '⚠️ ABDOMEN CHIRURGICAL POSSIBLE — avis chirurgical urgent',
  'priorite': 'critique'},
 {'code': 'EMBOLIE_PULMONAIRE',
  'symptomes': ['Dyspnée', 'Douleur thoracique', 'Douleur pleurale', 'Tachycardie', 'Hémoptysie', 'Hypoxie', 'Syncope'],
  'minimum': 3,
  'alerte': '⚠️ EMBOLIE PULMONAIRE POSSIBLE — urgence',
  'priorite': 'critique'},
 {'code': 'GROSSESSE_EXTRA_UTERINE',
  'symptomes': ['Douleurs pelviennes',
                'Douleur pelvienne brutale',
                'Saignements vaginaux',
                'Retard de règles',
                'Test grossesse positif',
                'Syncope',
                'Hypotension'],
  'minimum': 3,
  'alerte': '⚠️ GROSSESSE EXTRA-UTÉRINE POSSIBLE — urgence',
  'priorite': 'critique'},
 {'code': 'SEPSIS',
  'symptomes': ['Fièvre', 'Hypothermie', 'Tachycardie', 'Tachypnée', 'Confusion', 'Hypotension', 'Malaise'],
  'minimum': 3,
  'alerte': '⚠️ SEPSIS POSSIBLE — évaluation urgente',
  'priorite': 'critique'},
 {'code': 'DETRESSE_RESPIRATOIRE',
  'symptomes': ['Dyspnée',
                'Dyspnée au repos',
                'Impossibilité de parler',
                'Cyanose',
                'Hypoxie',
                'Tachypnée',
                'Tirage',
                'Signes de lutte respiratoire',
                'Détresse respiratoire'],
  'minimum': 2,
  'alerte': '⚠️ DÉTRESSE RESPIRATOIRE — urgence',
  'priorite': 'critique'},
 {'code': 'SUICIDE',
  'symptomes': ['Idées suicidaires', 'Plan suicidaire'],
  'minimum': 1,
  'alerte': '⚠️ RISQUE SUICIDAIRE — ne pas laisser seul, orientation urgente',
  'priorite': 'critique'},
 {'code': 'HYPOGLYCEMIE_GRAVE',
  'symptomes': ['Sueurs froides', 'Tremblements', 'Confusion', 'Convulsions', 'Perte de conscience', 'Malaise'],
  'minimum': 3,
  'alerte': '⚠️ HYPOGLYCÉMIE POSSIBLE — glycémie capillaire urgente si disponible',
  'priorite': 'haute'},
 {'code': 'DESHYDRATATION_ENFANT',
  'symptomes': ['Déshydratation', 'Oligurie', 'Somnolence excessive', 'Muqueuses sèches', 'Hypotension', 'Tachycardie'],
  'minimum': 2,
  'alerte': '⚠️ DÉSHYDRATATION POSSIBLE — risque élevé chez enfant/sujet fragile',
  'priorite': 'haute'},
 {'code': 'INTOX_CO',
  'symptomes': ['Maux de tête', 'Nausées', 'Vertiges', 'Confusion', 'Perte de conscience', 'Fatigue'],
  'minimum': 3,
  'alerte': '⚠️ INTOXICATION AU CO POSSIBLE — sortir du lieu, urgence si signes neuro',
  'priorite': 'haute'},
 {'code': 'QUEUE_DE_CHEVAL',
  'symptomes': ['Douleurs lombaires',
                'Sciatique',
                'Troubles sphinctériens',
                'Anesthésie en selle',
                'Faiblesse musculaire'],
  'minimum': 3,
  'alerte': '⚠️ SYNDROME DE LA QUEUE DE CHEVAL POSSIBLE — urgence neurochirurgicale',
  'priorite': 'critique'}]

def reconstruire_index() -> None:
    """Reconstruit tous les index après extension de la base."""
    global SYMPTOME_TO_IDX, NUM_FEATURES, MALADIE_TO_LABEL, LABEL_TO_MALADIE, NUM_CLASSES
    global _NORMALIZED_SYMPTOMS, _NORMALIZED_SYNONYMS

    SYMPTOME_TO_IDX = {s: i for i, s in enumerate(SYMPTOMES_CANONIQUES)}
    NUM_FEATURES = len(SYMPTOMES_CANONIQUES)

    MALADIE_TO_LABEL = {m["nom"]: i for i, m in enumerate(MALADIES)}
    LABEL_TO_MALADIE = {i: m["nom"] for i, m in enumerate(MALADIES)}
    NUM_CLASSES = len(MALADIES)

    _NORMALIZED_SYMPTOMS = {normaliser_texte(s): s for s in SYMPTOMES_CANONIQUES}
    _NORMALIZED_SYNONYMS = {normaliser_texte(k): v for k, v in SYNONYMES.items()}

def normaliser_texte(text: Any) -> str:
    """Normalise un texte: minuscules, accents retirés, espaces propres."""
    if text is None:
        return ""
    text = str(text).strip().lower()
    text = text.replace("œ", "oe").replace("æ", "ae")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def _clamp_float(value: Any, min_value: float = 0.0, max_value: float = 1.0, default: float = 0.0) -> float:
    try:
        x = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(x) or math.isinf(x):
        return default
    return max(min_value, min(max_value, x))

def _get_num(d: Optional[Dict[str, Any]], *keys: str) -> Optional[float]:
    if not d:
        return None
    normalized = {normaliser_texte(k): v for k, v in d.items()}
    for key in keys:
        nk = normaliser_texte(key)
        if nk in normalized:
            try:
                return float(normalized[nk])
            except (TypeError, ValueError):
                return None
    return None

# Création initiale des index.
reconstruire_index()

# ------------------------------------------------------------
# 5) Validation de qualité — à lancer au démarrage du backend.
# ------------------------------------------------------------

def validate_knowledge_base(raise_on_error: bool = False) -> Dict[str, Any]:
    symptom_set = set(SYMPTOMES_CANONIQUES)
    symptom_counts = Counter(SYMPTOMES_CANONIQUES)
    disease_counts = Counter(m.get("nom", "") for m in MALADIES)

    duplicate_symptoms = sorted([s for s, c in symptom_counts.items() if c > 1])
    duplicate_diseases = sorted([s for s, c in disease_counts.items() if c > 1 and s])

    missing_by_disease: Dict[str, List[str]] = {}
    invalid_weights: List[Dict[str, Any]] = []
    malformed_diseases: List[str] = []

    for maladie in MALADIES:
        nom = maladie.get("nom", "<sans_nom>")
        symptomes = maladie.get("symptomes")
        if not isinstance(symptomes, dict) or not symptomes:
            malformed_diseases.append(nom)
            continue

        missing = [s for s in symptomes.keys() if s not in symptom_set]
        if missing:
            missing_by_disease[nom] = missing

        for symptome, poids in symptomes.items():
            if not isinstance(poids, (int, float)) or not (0.0 <= float(poids) <= 1.0):
                invalid_weights.append({"maladie": nom, "symptome": symptome, "poids": poids})

    unknown_synonym_targets = sorted({
        target for target in SYNONYMES.values()
        if target not in symptom_set
    })

    unknown_red_flag_symptoms: Dict[str, List[str]] = {}
    for rule in RED_FLAGS_GLOBAUX:
        code = rule.get("code") or rule.get("alerte", "<red_flag>")
        rule_symptoms: List[str] = []
        rule_symptoms.extend(rule.get("symptomes_requis", []))
        rule_symptoms.extend(rule.get("symptomes", []))
        unknown = [s for s in rule_symptoms if s not in symptom_set]
        if unknown:
            unknown_red_flag_symptoms[str(code)] = unknown

    report = {
        "version": MEDIGO_KB_VERSION,
        "ok": not (
            duplicate_symptoms or duplicate_diseases or missing_by_disease
            or invalid_weights or malformed_diseases or unknown_synonym_targets
            or unknown_red_flag_symptoms
        ),
        "num_symptomes": NUM_FEATURES,
        "num_maladies": len(MALADIES),
        "num_categories": len(set(m.get("categorie", "inconnue") for m in MALADIES)),
        "duplicate_symptoms": duplicate_symptoms,
        "duplicate_diseases": duplicate_diseases,
        "missing_by_disease": missing_by_disease,
        "invalid_weights": invalid_weights,
        "malformed_diseases": malformed_diseases,
        "unknown_synonym_targets": unknown_synonym_targets,
        "unknown_red_flag_symptoms": unknown_red_flag_symptoms,
    }

    if raise_on_error and not report["ok"]:
        raise ValueError("Base MEDIGO invalide: " + json.dumps(report, ensure_ascii=False, indent=2))

    return report

# ------------------------------------------------------------
# 6) Mapping de symptômes libres -> symptômes canoniques.
# ------------------------------------------------------------

def mapper_symptome(symptome: Any, fuzzy: bool = True, cutoff: float = 0.84) -> Optional[str]:
    """Retourne le symptôme canonique ou None si non reconnu."""
    if symptome is None:
        return None

    raw = str(symptome).strip()
    if raw in SYMPTOME_TO_IDX:
        return raw

    n = normaliser_texte(raw)
    if not n:
        return None

    if n in _NORMALIZED_SYMPTOMS:
        return _NORMALIZED_SYMPTOMS[n]

    if n in _NORMALIZED_SYNONYMS:
        target = _NORMALIZED_SYNONYMS[n]
        return target if target in SYMPTOME_TO_IDX else None

    if not fuzzy:
        return None

    choices = list(_NORMALIZED_SYMPTOMS.keys()) + list(_NORMALIZED_SYNONYMS.keys())
    matches = difflib.get_close_matches(n, choices, n=1, cutoff=cutoff)
    if not matches:
        return None

    match = matches[0]
    if match in _NORMALIZED_SYMPTOMS:
        return _NORMALIZED_SYMPTOMS[match]

    target = _NORMALIZED_SYNONYMS.get(match)
    return target if target in SYMPTOME_TO_IDX else None

def normaliser_symptomes(symptomes: Iterable[Any], fuzzy: bool = True) -> Tuple[List[str], List[str]]:
    reconnus: List[str] = []
    inconnus: List[str] = []
    seen = set()

    for item in symptomes or []:
        mapped = mapper_symptome(item, fuzzy=fuzzy)
        if mapped:
            if mapped not in seen:
                reconnus.append(mapped)
                seen.add(mapped)
        else:
            value = str(item).strip()
            if value:
                inconnus.append(value)

    return reconnus, inconnus

# ------------------------------------------------------------
# 7) Ajout de symptômes depuis les constantes vitales.
# Le modèle XGBoost reçoit toujours un vecteur de symptômes.
# ------------------------------------------------------------

def symptomes_depuis_vitaux(vitaux: Optional[Dict[str, Any]]) -> List[str]:
    result: List[str] = []

    temp = _get_num(vitaux, "temperature", "température", "temperature_c", "temp")
    spo2 = _get_num(vitaux, "spo2", "spO2", "saturation", "saturation_o2")
    fc = _get_num(vitaux, "fc", "frequence_cardiaque", "fréquence cardiaque", "heart_rate", "pouls")
    fr = _get_num(vitaux, "fr", "frequence_respiratoire", "fréquence respiratoire", "respiratory_rate")
    pas = _get_num(vitaux, "pas", "systolique", "sbp", "tension_systolique")
    pad = _get_num(vitaux, "pad", "diastolique", "dbp", "tension_diastolique")

    if temp is not None:
        if temp >= 38.0:
            result.append("Fièvre")
        if temp >= 39.5:
            result.append("Hyperthermie")
        if temp < 35.0:
            result.append("Hypothermie")

    if spo2 is not None:
        if spo2 < 94:
            result.append("Hypoxie")
        if spo2 < 92:
            result.append("Saturation basse")
        if spo2 < 90:
            result.append("Détresse respiratoire")

    if fc is not None:
        if fc > 100:
            result.append("Tachycardie")
        if fc < 50:
            result.append("Bradycardie")

    if fr is not None:
        if fr > 22:
            result.append("Tachypnée")
        if fr >= 30:
            result.append("Détresse respiratoire")

    if pas is not None:
        if pas < 90:
            result.append("Hypotension")
        if pas >= 140:
            result.append("Hypertension")
    if pad is not None:
        if pad >= 90:
            result.append("Hypertension")

    # unique + existant dans la base
    out: List[str] = []
    seen = set()
    for s in result:
        if s in SYMPTOME_TO_IDX and s not in seen:
            out.append(s)
            seen.add(s)
    return out

def fusionner_symptomes_et_vitaux(
    symptomes: Iterable[Any],
    vitaux: Optional[Dict[str, Any]] = None,
    fuzzy: bool = True,
) -> Tuple[List[str], List[str]]:
    reconnus, inconnus = normaliser_symptomes(symptomes, fuzzy=fuzzy)
    seen = set(reconnus)
    for s in symptomes_depuis_vitaux(vitaux):
        if s not in seen:
            reconnus.append(s)
            seen.add(s)
    return reconnus, inconnus

# ------------------------------------------------------------
# 8) Vectorisation XGBoost.
# ------------------------------------------------------------

def vectoriser_symptomes(
    symptomes: Iterable[Any],
    vitaux: Optional[Dict[str, Any]] = None,
    intensites: Optional[Dict[str, float]] = None,
    fuzzy: bool = True,
    as_numpy: bool = False,
    return_unknowns: bool = False,
) -> Any:
    reconnus, inconnus = fusionner_symptomes_et_vitaux(symptomes, vitaux=vitaux, fuzzy=fuzzy)
    vec = [0.0] * NUM_FEATURES

    normalized_intensites: Dict[str, float] = {}
    for key, val in (intensites or {}).items():
        mapped = mapper_symptome(key, fuzzy=fuzzy)
        if mapped:
            normalized_intensites[mapped] = _clamp_float(val, 0.0, 1.0, default=1.0)

    for s in reconnus:
        idx = SYMPTOME_TO_IDX[s]
        vec[idx] = max(vec[idx], normalized_intensites.get(s, 1.0))

    if as_numpy:
        try:
            import numpy as np
            vec_out: Any = np.array(vec, dtype="float32")
        except Exception:
            vec_out = vec
    else:
        vec_out = vec

    if return_unknowns:
        return {"vector": vec_out, "symptomes_reconnus": reconnus, "symptomes_inconnus": inconnus}
    return vec_out

def get_feature_names() -> List[str]:
    return list(SYMPTOMES_CANONIQUES)

def get_label_maps() -> Dict[str, Any]:
    return {
        "maladie_to_label": dict(MALADIE_TO_LABEL),
        "label_to_maladie": dict(LABEL_TO_MALADIE),
        "num_classes": NUM_CLASSES,
    }

# ------------------------------------------------------------
# 9) Red flags et triage.
# ------------------------------------------------------------

_PRIORITY_ORDER = {"critique": 0, "haute": 1, "moyenne": 2, "basse": 3}

def detecter_red_flags(
    symptomes: Iterable[Any],
    vitaux: Optional[Dict[str, Any]] = None,
    fuzzy: bool = True,
) -> List[Dict[str, Any]]:
    reconnus, _ = fusionner_symptomes_et_vitaux(symptomes, vitaux=vitaux, fuzzy=fuzzy)
    present = set(reconnus)
    alerts: List[Dict[str, Any]] = []

    for rule in RED_FLAGS_GLOBAUX:
        required = set(rule.get("symptomes_requis", []))
        pool = list(rule.get("symptomes", []))
        minimum = int(rule.get("minimum", len(pool)))

        if required and not required.issubset(present):
            continue

        matched = [s for s in pool if s in present]
        if len(matched) >= minimum:
            alerts.append({
                "code": rule.get("code", "RED_FLAG"),
                "alerte": rule.get("alerte", "Red flag détecté"),
                "priorite": rule.get("priorite", "haute"),
                "symptomes_declencheurs": sorted(list(required)) + matched,
            })

    # Alertes directes depuis vitaux.
    spo2 = _get_num(vitaux, "spo2", "saturation", "saturation_o2")
    pas = _get_num(vitaux, "pas", "systolique", "sbp", "tension_systolique")
    fc = _get_num(vitaux, "fc", "frequence_cardiaque", "heart_rate", "pouls")
    fr = _get_num(vitaux, "fr", "frequence_respiratoire", "respiratory_rate")
    temp = _get_num(vitaux, "temperature", "température", "temperature_c", "temp")

    if spo2 is not None and spo2 < 92:
        alerts.append({
            "code": "VITAL_SPO2",
            "alerte": "⚠️ SpO2 < 92% — hypoxie significative",
            "priorite": "critique",
            "symptomes_declencheurs": ["Hypoxie", "Saturation basse"],
        })
    if pas is not None and pas < 90:
        alerts.append({
            "code": "VITAL_HYPOTENSION",
            "alerte": "⚠️ PAS < 90 mmHg — hypotension/choc possible",
            "priorite": "critique",
            "symptomes_declencheurs": ["Hypotension"],
        })
    if fr is not None and fr >= 30:
        alerts.append({
            "code": "VITAL_TACHYPNEE",
            "alerte": "⚠️ FR ≥ 30/min — détresse respiratoire ou sepsis possible",
            "priorite": "haute",
            "symptomes_declencheurs": ["Tachypnée"],
        })
    if fc is not None and fc >= 130:
        alerts.append({
            "code": "VITAL_TACHYCARDIE",
            "alerte": "⚠️ FC ≥ 130/min — évaluation urgente selon contexte",
            "priorite": "haute",
            "symptomes_declencheurs": ["Tachycardie"],
        })
    if temp is not None and temp >= 40:
        alerts.append({
            "code": "VITAL_HYPERTHERMIE",
            "alerte": "⚠️ Température ≥ 40°C — hyperthermie sévère",
            "priorite": "haute",
            "symptomes_declencheurs": ["Hyperthermie"],
        })

    # Déduplication par code.
    dedup: Dict[str, Dict[str, Any]] = {}
    for alert in alerts:
        code = alert["code"]
        if code not in dedup:
            dedup[code] = alert
    return sorted(dedup.values(), key=lambda a: _PRIORITY_ORDER.get(a.get("priorite", "haute"), 9))

def orientation_triage(red_flags: Sequence[Dict[str, Any]]) -> Dict[str, str]:
    if any(a.get("priorite") == "critique" for a in red_flags):
        return {
            "niveau": "urgence_immediate",
            "message": "Red flag critique détecté: orienter vers les urgences / SAMU selon disponibilité locale.",
        }
    if any(a.get("priorite") == "haute" for a in red_flags):
        return {
            "niveau": "avis_medical_urgent",
            "message": "Red flag important détecté: avis médical rapide recommandé.",
        }
    return {
        "niveau": "orientation_standard",
        "message": "Pas de red flag global détecté par les règles; poursuivre l'interrogatoire clinique.",
    }

# ------------------------------------------------------------
# 10) Score différentiel rule-based.
# Utile en fallback, en explication, ou pour générer des cas synthétiques.
# ------------------------------------------------------------

def scorer_maladie(maladie: Dict[str, Any], symptomes_reconnus: Iterable[str]) -> Dict[str, Any]:
    present = set(symptomes_reconnus)
    weights: Dict[str, float] = maladie.get("symptomes", {})
    total_weight = sum(float(w) for w in weights.values()) or 1.0

    matched = {s: float(w) for s, w in weights.items() if s in present}
    matched_weight = sum(matched.values())

    coverage = matched_weight / total_weight
    matched_count = len(matched)
    extra_count = max(0, len(present) - matched_count)

    # Bonus modéré si plusieurs symptômes concordent, pénalité légère si entrée très bruitée.
    score = coverage * (1.0 + min(matched_count, 8) * 0.025) - min(extra_count * 0.01, 0.15)
    score = _clamp_float(score, 0.0, 1.0)

    missing_important = [
        s for s, w in sorted(weights.items(), key=lambda item: item[1], reverse=True)
        if s not in present and float(w) >= 0.65
    ][:6]

    return {
        "maladie": maladie.get("nom"),
        "categorie": maladie.get("categorie"),
        "score": round(score, 4),
        "urgence": bool(maladie.get("urgence", False)),
        "priorite_maroc": maladie.get("priorite_maroc", "standard"),
        "symptomes_correspondants": sorted(matched.keys()),
        "symptomes_importants_manquants": missing_important,
        "red_flags_maladie": maladie.get("red_flags", []),
        "questions": maladie.get("questions", []),
    }

def scorer_diagnostics(
    symptomes: Iterable[Any],
    vitaux: Optional[Dict[str, Any]] = None,
    top_k: int = 10,
    fuzzy: bool = True,
    categorie: Optional[str] = None,
) -> List[Dict[str, Any]]:
    reconnus, _ = fusionner_symptomes_et_vitaux(symptomes, vitaux=vitaux, fuzzy=fuzzy)

    candidats = MALADIES
    if categorie:
        cat_norm = normaliser_texte(categorie)
        candidats = [m for m in MALADIES if normaliser_texte(m.get("categorie")) == cat_norm]

    scores = [scorer_maladie(m, reconnus) for m in candidats]
    scores.sort(key=lambda x: (x["score"], x["urgence"]), reverse=True)
    return scores[:max(1, int(top_k))]

def questions_suivantes(hypotheses: Sequence[Dict[str, Any]], max_questions: int = 8) -> List[str]:
    questions: List[str] = []
    seen = set()
    for h in hypotheses:
        for q in h.get("questions", []):
            if q not in seen:
                questions.append(q)
                seen.add(q)
            if len(questions) >= max_questions:
                return questions
    return questions

def diagnostiquer(
    symptomes: Iterable[Any],
    vitaux: Optional[Dict[str, Any]] = None,
    top_k: int = 5,
    fuzzy: bool = True,
    include_vector: bool = False,
) -> Dict[str, Any]:
    """
    Sortie pour ton backend:
    - symptomes_reconnus / inconnus
    - red_flags prioritaires
    - orientation
    - hypothèses différentielles
    - questions à poser
    - vecteur XGBoost optionnel
    """
    reconnus, inconnus = fusionner_symptomes_et_vitaux(symptomes, vitaux=vitaux, fuzzy=fuzzy)
    red_flags = detecter_red_flags(reconnus, vitaux=vitaux, fuzzy=False)
    hypotheses = scorer_diagnostics(reconnus, vitaux=None, top_k=top_k, fuzzy=False)
    result: Dict[str, Any] = {
        "version": MEDIGO_KB_VERSION,
        "symptomes_reconnus": reconnus,
        "symptomes_inconnus": inconnus,
        "red_flags": red_flags,
        "orientation": orientation_triage(red_flags),
        "hypotheses": hypotheses,
        "questions_suivantes": questions_suivantes(hypotheses),
        "message_securite": (
            "Ce module aide au triage et au diagnostic différentiel. "
            "Il ne remplace pas une décision médicale validée par un professionnel."
        ),
    }
    if include_vector:
        result["vecteur_xgboost"] = vectoriser_symptomes(reconnus, vitaux=None, fuzzy=False)
    return result

# ------------------------------------------------------------
# 11) Génération de données synthétiques pour bootstrapping XGBoost.
# À remplacer/compléter par données réelles validées médecin.
# ------------------------------------------------------------

def generer_cas_synthetiques(
    n_par_maladie: int = 80,
    seed: int = 42,
    bruit: float = 0.03,
    min_symptomes: int = 2,
) -> Dict[str, Any]:
    rng = random.Random(seed)
    X: List[List[float]] = []
    y: List[int] = []
    meta: List[Dict[str, Any]] = []

    for maladie in MALADIES:
        nom = maladie["nom"]
        label = MALADIE_TO_LABEL[nom]
        weights = maladie.get("symptomes", {})
        high_yield = [s for s, w in sorted(weights.items(), key=lambda item: item[1], reverse=True)]

        for _ in range(max(1, int(n_par_maladie))):
            selected: List[str] = []
            for symptome, proba in weights.items():
                p = _clamp_float(float(proba) * rng.uniform(0.75, 1.15), 0.02, 0.98)
                if rng.random() < p:
                    selected.append(symptome)

            for s in high_yield:
                if len(selected) >= min_symptomes:
                    break
                if s not in selected:
                    selected.append(s)

            # Bruit léger: symptômes aléatoires pour éviter un modèle trop rigide.
            if rng.random() < bruit:
                selected.append(rng.choice(SYMPTOMES_CANONIQUES))
            if rng.random() < bruit / 2:
                selected.append(rng.choice(SYMPTOMES_CANONIQUES))

            selected = list(dict.fromkeys(selected))
            X.append(vectoriser_symptomes(selected, fuzzy=False))
            y.append(label)
            meta.append({
                "maladie": nom,
                "label": label,
                "categorie": maladie.get("categorie"),
                "symptomes": selected,
            })

    return {
        "X": X,
        "y": y,
        "feature_names": get_feature_names(),
        "label_to_maladie": dict(LABEL_TO_MALADIE),
        "maladie_to_label": dict(MALADIE_TO_LABEL),
        "meta": meta,
    }

def exporter_kb_json(path: str) -> None:
    payload = {
        "version": MEDIGO_KB_VERSION,
        "symptomes_canoniques": SYMPTOMES_CANONIQUES,
        "maladies": MALADIES,
        "red_flags_globaux": RED_FLAGS_GLOBAUX,
        "synonymes": SYNONYMES,
        "label_to_maladie": LABEL_TO_MALADIE,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

def resume_kb() -> Dict[str, Any]:
    cats = Counter(m.get("categorie", "inconnue") for m in MALADIES)
    return {
        "version": MEDIGO_KB_VERSION,
        "num_symptomes": NUM_FEATURES,
        "num_maladies": len(MALADIES),
        "num_red_flags": len(RED_FLAGS_GLOBAUX),
        "categories": dict(sorted(cats.items())),
    }

__all__ = [
    "MEDIGO_KB_VERSION",
    "SYMPTOMES_CANONIQUES",
    "SYMPTOME_TO_IDX",
    "NUM_FEATURES",
    "MALADIES",
    "MALADIE_TO_LABEL",
    "LABEL_TO_MALADIE",
    "NUM_CLASSES",
    "SYNONYMES",
    "RED_FLAGS_GLOBAUX",
    "validate_knowledge_base",
    "normaliser_texte",
    "mapper_symptome",
    "normaliser_symptomes",
    "symptomes_depuis_vitaux",
    "fusionner_symptomes_et_vitaux",
    "vectoriser_symptomes",
    "get_feature_names",
    "get_label_maps",
    "detecter_red_flags",
    "orientation_triage",
    "scorer_maladie",
    "scorer_diagnostics",
    "questions_suivantes",
    "diagnostiquer",
    "generer_cas_synthetiques",
    "exporter_kb_json",
    "resume_kb",
]


# ------------------------------------------------------------
# 12) Hotfix V2.0.1: Purpura + SCA avec essoufflement/nausées.
# ------------------------------------------------------------

MEDIGO_KB_VERSION = "2.0.1-maroc-fr"
_extend_unique(SYMPTOMES_CANONIQUES, ["Purpura"])
for _rule in RED_FLAGS_GLOBAUX:
    if _rule.get("code") == "SCA":
        _rule["symptomes"] = [
            "Douleur thoracique", "Oppression thoracique", "Douleur thoracique constrictive",
            "Dyspnée", "Essoufflement", "Sueurs froides", "Irradiation bras gauche",
            "Douleur mâchoire", "Syncope", "Nausées",
        ]
        _rule["minimum"] = 3
reconstruire_index()

if __name__ == "__main__":
    report = validate_knowledge_base(raise_on_error=False)
    print(json.dumps(resume_kb(), ensure_ascii=False, indent=2))
    if not report["ok"]:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    demo = diagnostiquer(
        ["douleur poitrine", "sueurs froides", "essoufflement", "nausée"],
        vitaux={"spo2": 91, "fc": 122},
        top_k=5,
        include_vector=False,
    )
    print(json.dumps(demo, ensure_ascii=False, indent=2))

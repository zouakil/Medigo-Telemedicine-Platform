"""
MEDIGO - Système de traductions FR / AR pour l'interface patient
Dictionnaire centralisé de toutes les chaînes traduites
"""

TRANSLATIONS = {
    # ============================================================
    # PAGE CHOIX LANGUE
    # ============================================================
    'choose_language': {
        'fr': 'Veuillez choisir votre langue',
        'ar': 'المرجو اختيار اللغة',
    },
    'french': {
        'fr': 'Français',
        'ar': 'الفرنسية',
    },
    'arabic': {
        'fr': 'العربية',
        'ar': 'العربية',
    },

    # ============================================================
    # LOGIN
    # ============================================================
    'enter_code': {
        'fr': 'Entrez votre code',
        'ar': 'أدخل الرمز الخاص بك',
    },
    'unique_code': {
        'fr': 'Code unique',
        'ar': 'الرمز المميز',
    },
    'login_btn': {
        'fr': 'Se connecter',
        'ar': 'تسجيل الدخول',
    },
    'incorrect_code': {
        'fr': 'Code incorrect. Veuillez réessayer.',
        'ar': 'الرمز غير صحيح. يرجى المحاولة مرة أخرى.',
    },
    'access_denied': {
        'fr': 'Accès refusé. Votre compte a été désactivé. Veuillez contacter l\'administration.',
        'ar': 'تم رفض الوصول. تم تعطيل حسابك. يرجى الاتصال بالإدارة.',
    },

    # ============================================================
    # MENU PRINCIPAL
    # ============================================================
    'welcome': {
        'fr': 'Bienvenue',
        'ar': 'مرحباً',
    },
    'home': {
        'fr': 'Accueil',
        'ar': 'الرئيسية',
    },
    'consultation': {
        'fr': 'Consultation',
        'ar': 'استشارة',
    },
    'new_consultation': {
        'fr': 'Nouvelle consultation',
        'ar': 'استشارة جديدة',
    },
    'start_consultation': {
        'fr': 'Démarrer une consultation',
        'ar': 'بدء استشارة',
    },
    'medical_alert': {
        'fr': 'ALERTE MÉDECIN',
        'ar': 'تنبيه الطبيب',
    },
    'history': {
        'fr': 'Historique',
        'ar': 'السجل',
    },
    'consultations_history': {
        'fr': 'Historique consultations',
        'ar': 'سجل الاستشارات',
    },
    'prescriptions': {
        'fr': 'Ordonnances',
        'ar': 'الوصفات الطبية',
    },
    'vital_signs': {
        'fr': 'Signes vitaux',
        'ar': 'العلامات الحيوية',
    },
    'logout': {
        'fr': 'Déconnexion',
        'ar': 'تسجيل الخروج',
    },

    # ============================================================
    # CONSULTATION
    # ============================================================
    'doctor_search': {
        'fr': 'Recherche d\'un médecin...',
        'ar': 'البحث عن طبيب...',
    },
    'no_doctor_available': {
        'fr': 'Aucun médecin disponible pour le moment',
        'ar': 'لا يوجد طبيب متاح حالياً',
    },
    'try_again_later': {
        'fr': 'Veuillez réessayer plus tard',
        'ar': 'يرجى المحاولة لاحقاً',
    },
    'cancel': {
        'fr': 'Annuler',
        'ar': 'إلغاء',
    },
    'waiting_doctor': {
        'fr': 'En attente d\'un médecin...',
        'ar': 'في انتظار الطبيب...',
    },
    'doctor_accepted': {
        'fr': 'Le médecin a accepté votre consultation',
        'ar': 'قبل الطبيب استشارتك',
    },
    'consultation_starting': {
        'fr': 'Consultation en cours de démarrage...',
        'ar': 'بدء الاستشارة...',
    },

    # ============================================================
    # LIVE CONSULTATION
    # ============================================================
    'live_consultation': {
        'fr': 'Consultation en direct',
        'ar': 'استشارة مباشرة',
    },
    'mic_on': {
        'fr': 'Micro activé',
        'ar': 'الميكروفون مفعل',
    },
    'mic_off': {
        'fr': 'Micro désactivé',
        'ar': 'الميكروفون معطل',
    },
    'camera_on': {
        'fr': 'Caméra activée',
        'ar': 'الكاميرا مفعلة',
    },
    'camera_off': {
        'fr': 'Caméra désactivée',
        'ar': 'الكاميرا معطلة',
    },
    'end_call': {
        'fr': 'Terminer l\'appel',
        'ar': 'إنهاء المكالمة',
    },
    'chat': {
        'fr': 'Chat',
        'ar': 'الدردشة',
    },
    'send_message': {
        'fr': 'Envoyer un message',
        'ar': 'إرسال رسالة',
    },
    'type_message': {
        'fr': 'Tapez votre message...',
        'ar': 'اكتب رسالتك...',
    },

    # ============================================================
    # SIGNES VITAUX
    # ============================================================
    'my_vital_signs': {
        'fr': 'Mes signes vitaux',
        'ar': 'علاماتي الحيوية',
    },
    'last_measurements': {
        'fr': 'Dernières mesures',
        'ar': 'آخر القياسات',
    },
    'no_measurements': {
        'fr': 'Aucune mesure disponible',
        'ar': 'لا توجد قياسات متاحة',
    },
    'data_after_consultation': {
        'fr': 'Les données apparaîtront après votre prochaine consultation',
        'ar': 'ستظهر البيانات بعد استشارتك القادمة',
    },
    'spo2_evolution': {
        'fr': 'Évolution SpO2',
        'ar': 'تطور تشبع الأكسجين',
    },
    'hr_evolution': {
        'fr': 'Évolution FC (bpm)',
        'ar': 'تطور النبض (نبضة/د)',
    },
    'temp_evolution': {
        'fr': 'Évolution Température',
        'ar': 'تطور درجة الحرارة',
    },
    'no_spo2_data': {
        'fr': 'Aucune donnée SpO2 disponible',
        'ar': 'لا توجد بيانات تشبع الأكسجين',
    },
    'no_hr_data': {
        'fr': 'Aucune donnée de fréquence cardiaque disponible',
        'ar': 'لا توجد بيانات النبض',
    },
    'no_temp_data': {
        'fr': 'Aucune donnée de température disponible',
        'ar': 'لا توجد بيانات درجة الحرارة',
    },

    # ============================================================
    # HISTORIQUE
    # ============================================================
    'consultation_date': {
        'fr': 'Date de consultation',
        'ar': 'تاريخ الاستشارة',
    },
    'doctor': {
        'fr': 'Médecin',
        'ar': 'الطبيب',
    },
    'diagnosis': {
        'fr': 'Diagnostic',
        'ar': 'التشخيص',
    },
    'no_consultations': {
        'fr': 'Aucune consultation enregistrée',
        'ar': 'لا توجد استشارات مسجلة',
    },
    'view_details': {
        'fr': 'Voir détails',
        'ar': 'عرض التفاصيل',
    },

    # ============================================================
    # ORDONNANCES
    # ============================================================
    'my_prescriptions': {
        'fr': 'Mes ordonnances',
        'ar': 'وصفاتي الطبية',
    },
    'prescription_date': {
        'fr': 'Date',
        'ar': 'التاريخ',
    },
    'no_prescriptions': {
        'fr': 'Aucune ordonnance disponible',
        'ar': 'لا توجد وصفات طبية متاحة',
    },
    'view_prescription': {
        'fr': 'Voir l\'ordonnance',
        'ar': 'عرض الوصفة',
    },
    'download_pdf': {
        'fr': 'Télécharger PDF',
        'ar': 'تحميل PDF',
    },
    'medication': {
        'fr': 'Médicament',
        'ar': 'الدواء',
    },
    'dosage': {
        'fr': 'Posologie',
        'ar': 'الجرعة',
    },
    'duration': {
        'fr': 'Durée',
        'ar': 'المدة',
    },
    'verify_prescription': {
        'fr': 'Vérifier ordonnance',
        'ar': 'التحقق من الوصفة',
    },

    # ============================================================
    # ATTENTE / FIN CONSULTATION
    # ============================================================
    'waiting_prescription': {
        'fr': 'Le médecin prépare votre ordonnance...',
        'ar': 'الطبيب يحضر وصفتك الطبية...',
    },
    'consultation_finished': {
        'fr': 'Consultation terminée',
        'ar': 'انتهت الاستشارة',
    },
    'thank_you': {
        'fr': 'Merci pour votre confiance',
        'ar': 'شكراً لثقتكم',
    },
    'back_to_menu': {
        'fr': 'Retour au menu',
        'ar': 'العودة إلى القائمة',
    },

    # ============================================================
    # COMMUN
    # ============================================================
    'loading': {
        'fr': 'Chargement...',
        'ar': 'جاري التحميل...',
    },
    'error': {
        'fr': 'Erreur',
        'ar': 'خطأ',
    },
    'success': {
        'fr': 'Succès',
        'ar': 'نجاح',
    },
    'confirm': {
        'fr': 'Confirmer',
        'ar': 'تأكيد',
    },
    'yes': {
        'fr': 'Oui',
        'ar': 'نعم',
    },
    'no': {
        'fr': 'Non',
        'ar': 'لا',
    },
    'language': {
        'fr': 'Langue',
        'ar': 'اللغة',
    },
    'change_language': {
        'fr': 'Changer la langue',
        'ar': 'تغيير اللغة',
    },

    'my_history': {
        'fr': 'Mon historique',
        'ar': 'سجلي الطبي',
    },
    'closed': {
        'fr': 'Clôturée',
        'ar': 'مكتملة',
    },
    'symptoms': {
        'fr': 'Symptômes',
        'ar': 'الأعراض',
    },
    'diagnosed_diseases': {
        'fr': 'Maladies diagnostiquées',
        'ar': 'الأمراض المشخصة',
    },
    'no_symptoms_diseases': {
        'fr': 'Aucun symptôme ou maladie enregistré',
        'ar': 'لم يتم تسجيل أعراض أو أمراض',
    },
    'no_past_consultations': {
        'fr': 'Aucune consultation passée',
        'ar': 'لا توجد استشارات سابقة',
    },
    'history_will_appear': {
        'fr': 'Votre historique apparaîtra ici',
        'ar': 'سيظهر سجلك هنا',
    },
    'prescription_label': {
        'fr': 'Ordonnance',
        'ar': 'وصفة طبية',
    },
    'no_prescription_short': {
        'fr': 'Aucune ordonnance',
        'ar': 'لا توجد وصفات طبية',
    },
    'prescriptions_will_appear': {
        'fr': 'Vos ordonnances apparaîtront ici',
        'ar': 'ستظهر وصفاتك الطبية هنا',
    },
    'thanks_medigo': {
        'fr': 'Merci d\'avoir utilisé Medigo.',
        'ar': 'شكراً لاستخدامك ميديغو.',
    },
    'take_care': {
        'fr': 'Prenez soin de vous !',
        'ar': 'اعتنِ بنفسك !',
    },
    'back_home': {
        'fr': 'Retour à l\'accueil',
        'ar': 'العودة إلى الرئيسية',
    },
    'get_well': {
        'fr': 'Bon rétablissement',
        'ar': 'تمنياتنا بالشفاء العاجل',
    },
    'reconsult_advice': {
        'fr': 'N\'hésitez pas à reconsulter si vos symptômes persistent ou s\'aggravent.',
        'ar': 'لا تتردد في الاستشارة مرة أخرى إذا استمرت أو تفاقمت الأعراض.',
    },
    'preparing_prescription': {
        'fr': 'Préparation de votre ordonnance',
        'ar': 'جاري تحضير وصفتك الطبية',
    },
    'please_wait': {
        'fr': 'Veuillez patienter quelques instants...',
        'ar': 'يرجى الانتظار قليلاً...',
    },
    'verify_code': {
        'fr': 'Code de vérification',
        'ar': 'رمز التحقق',
    },
    'enter_verification_code': {
        'fr': 'Entrez le code de vérification',
        'ar': 'أدخل رمز التحقق',
    },
    'verify': {
        'fr': 'Vérifier',
        'ar': 'تحقق',
    },
    'invalid_code': {
        'fr': 'Code invalide',
        'ar': 'رمز غير صالح',
    },
    'my_prescription': {
        'fr': 'Mon ordonnance',
        'ar': 'وصفتي الطبية',
    },
    'date': {
        'fr': 'Date',
        'ar': 'التاريخ',
    },
    'prescription': {
        'fr': 'Prescription',
        'ar': 'الوصفة',
    },
    'qr_code': {
        'fr': 'QR Code',
        'ar': 'رمز QR',
    },
    'scan_to_download': {
        'fr': 'Scannez pour télécharger',
        'ar': 'امسح للتحميل',
    },
    'connecting': {
        'fr': 'Connexion',
        'ar': 'جاري الاتصال',
    },
    'you': {
        'fr': 'Vous',
        'ar': 'أنت',
    },
    'mic_muted': {
        'fr': 'Micro coupé',
        'ar': 'الميكروفون مكتوم',
    },
    'spo2_measure': {
        'fr': 'Mesure SpO2 & Fréquence cardiaque',
        'ar': 'قياس تشبع الأكسجين والنبض',
    },
    'spo2_instruction': {
        'fr': 'Placez votre index ou majeur sur le capteur rouge et maintenez sans bouger.',
        'ar': 'ضع إصبع السبابة أو الوسطى على المستشعر الأحمر وحافظ على عدم الحركة.',
    },
    'temp_measure': {
        'fr': 'Mesure de température',
        'ar': 'قياس درجة الحرارة',
    },
    'temp_instruction': {
        'fr': 'Pointez le capteur infrarouge vers votre front à environ 5 cm de distance.',
        'ar': 'وجه مستشعر الأشعة تحت الحمراء نحو جبهتك على بعد حوالي 5 سم.',
    },
    'fullscreen': {
        'fr': 'Plein écran',
        'ar': 'ملء الشاشة',
    },
    'message_placeholder': {
        'fr': 'Message...',
        'ar': 'رسالة...',
    },
    'image': {
        'fr': 'Image',
        'ar': 'صورة',
    },
    'camera_unavailable': {
        'fr': 'Caméra indisponible',
        'ar': 'الكاميرا غير متوفرة',
    },
    'understood': {
        'fr': 'J\'ai compris',
        'ar': 'فهمت',
    },
    'connected': {
        'fr': 'Connecté',
        'ar': 'متصل',
    },
    'waiting_doctor_join': {
        'fr': 'En attente du médecin',
        'ar': 'في انتظار الطبيب',
    },
    'camera_muted': {
        'fr': 'Caméra coupée',
        'ar': 'الكاميرا مغلقة',
    },
}


def get_translation(key, lang='fr'):
    """Récupère la traduction pour une clé donnée."""
    if key not in TRANSLATIONS:
        return key  # Fallback: retourne la clé si pas trouvée
    return TRANSLATIONS[key].get(lang, TRANSLATIONS[key].get('fr', key))


def is_rtl(lang):
    """Retourne True si la langue est de droite à gauche."""
    return lang == 'ar'

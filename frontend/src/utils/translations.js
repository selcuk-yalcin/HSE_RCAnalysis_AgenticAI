const translations = {
  tr: {
    // Header
    interactive_mode: 'Etkileşimli Sohbet',
    batch_mode: 'Toplu Analiz',
    
    // Chat Interface
    analysis_steps: 'AKIŞ ADIMLARI',
    step_1: '1. Olay Metni Alındı',
    step_1_desc: 'İş kazası açıklaması kaydedildi',
    step_2: '2. İlk Analiz Tamamlandı',
    step_2_desc: 'Temel bilgiler çıkarıldı',
    step_3: '3. Kök Neden Analizi',
    step_3_desc: 'Derinlemesine analiz yapılıyor',
    step_4: '4. Rapor Hazırlanıyor',
    step_4_desc: 'Sonuçlar derleniyor',
    
    welcome_message: 'Merhaba! İş kazası analizi için size yardımcı olacağım. Lütfen kazayı detaylı bir şekilde anlatın.',
    input_placeholder: 'Mesajınızı yazın...',
    input_hint: 'Enter ile gönder, Shift+Enter ile yeni satır',
    reset: 'Sıfırla',
    export: 'Dışa Aktar',
    attach_file: 'Dosya Ekle',
    
    analysis_started: 'Analiz başlatıldı. Sonuçlar hazır olduğunda bilgilendirileceğiniz.',
    error_occurred: 'Bir hata oluştu',
    
    // Questions
    q_fall_protection: 'İşkelede düşme koruması var mıydı?',
    q_safety_harness: 'Çalışan emniyet kemeri takıyor muydu?',
    q_safety_training: 'Çalışan yüksekte çalışma eğitimi almış mıydı?',
    q_location: 'Kaza nerede gerçekleşti?',
    q_time: 'Kaza ne zaman meydana geldi?',
    q_witnesses: 'Olayın tanıkları var mı?',
    
    // Options
    yes: 'Evet',
    no: 'Hayır',
    unknown: 'Bilinmiyor',
    partial: 'Kısmen',
    type_answer: 'Cevabınızı yazın...',
    
    // Incident Form
    incident_report_form: 'İş Kazası Rapor Formu',
    form_subtitle: 'HSG245 standartlarına göre detaylı kaza raporu',
    
    // Sections
    section_reporter: 'Bildirim Yapan Kişi',
    section_incident_details: 'Kaza Detayları',
    section_description: 'Olay Açıklaması (5W1H)',
    section_safety_equipment: 'Güvenlik Ekipmanları',
    section_witnesses: 'Tanıklar',
    section_environment: 'Çevresel Koşullar',
    section_work_conditions: 'Çalışma Koşulları',
    section_injuries: 'Yaralanma / Hasar',
    section_root_cause: 'Kök Neden ve Önleyici Aksiyonlar',
    
    // Fields
    reported_by: 'Bildiren',
    report_date: 'Bildirim Tarihi',
    report_time: 'Bildirim Saati',
    incident_date: 'Kaza Tarihi',
    incident_time: 'Kaza Saati',
    location: 'Konum',
    department: 'Departman',
    event_category: 'Olay Kategorisi',
    
    incident: 'Kaza',
    near_miss: 'Ramak Kala Olay',
    unsafe_condition: 'Güvensiz Durum',
    property_damage: 'Maddi Hasar',
    
    incident_description: 'Olay Açıklaması',
    what_where_when_who: 'Ne oldu, Nerede, Ne zaman, Kim',
    describe_incident_detail: 'Kazayı detaylı bir şekilde anlatın...',
    include_details_hint: 'Lütfen ne, nerede, ne zaman, kim, nasıl ve neden bilgilerini ekleyin',
    
    what_happened: 'Ne Oldu?',
    where_happened: 'Nerede Oldu?',
    when_happened: 'Ne Zaman Oldu?',
    who_involved: 'Kimler Dahil?',
    emergency_measures: 'Acil Önlemler',
    
    what_placeholder: 'Gerçekleşen olayı tanımlayın',
    where_placeholder: 'Tam konum ve çalışma alanı',
    when_placeholder: 'Tarih, saat ve vardiya bilgisi',
    who_placeholder: 'İlgili kişiler ve görevleri',
    emergency_placeholder: 'Olay sonrası alınan önlemler',
    
    fall_protection_present: 'Düşme Koruması Var mıydı?',
    safety_harness_worn: 'Emniyet Kemeri Takılı mıydı?',
    safety_training_received: 'Güvenlik Eğitimi Alındı mı?',
    ppe_used: 'Kullanılan KKD',
    ppe_placeholder: 'Baret, eldiven, ayakkabı vb.',
    
    witnesses_present: 'Tanık Var mı?',
    witness_names: 'Tanık İsimleri',
    witness_statements: 'Tanık İfadeleri',
    witness_names_placeholder: 'İsim, görev ve iletişim bilgisi',
    witness_statements_placeholder: 'Tanıkların gözlemleri',
    
    weather_conditions: 'Hava Koşulları',
    lighting_conditions: 'Aydınlatma',
    noise_level: 'Gürültü Seviyesi',
    temperature: 'Sıcaklık',
    
    weather_placeholder: 'Güneşli, yağmurlu, rüzgarlı vb.',
    lighting_placeholder: 'İyi, kötü, yeterli vb.',
    noise_placeholder: 'Yüksek, normal, düşük',
    temperature_placeholder: 'Derece (°C)',
    
    work_type: 'İş Türü',
    work_height: 'Çalışma Yüksekliği',
    experience_level: 'Deneyim Seviyesi',
    shift_time: 'Vardiya',
    work_duration: 'Çalışma Süresi',
    
    work_type_placeholder: 'Montaj, bakım, taşıma vb.',
    work_height_placeholder: 'Metre cinsinden',
    experience_placeholder: 'Yıl cinsinden',
    shift_placeholder: 'Sabah, öğle, gece',
    
    injury_type: 'Yaralanma Türü',
    injury_severity: 'Yaralanma Şiddeti',
    body_part: 'Yaralanan Bölge',
    medical_treatment: 'Tıbbi Müdahale',
    property_damage: 'Maddi Hasar',
    
    injury_type_placeholder: 'Kesik, kırık, ezilme vb.',
    body_part_placeholder: 'Baş, kol, bacak vb.',
    medical_placeholder: 'İlk yardım, hastane vb.',
    
    minor: 'Hafif',
    moderate: 'Orta',
    severe: 'Ciddi',
    fatal: 'Ölümcül',
    
    root_cause_initial: 'Kök Neden (İlk Değerlendirme)',
    corrective_actions: 'Düzeltici Aksiyonlar',
    additional_notes: 'Ek Notlar',
    
    root_cause_placeholder: 'Kazanın temel nedenleri nelerdir?',
    corrective_placeholder: 'Önerilen önleyici tedbirler',
    notes_placeholder: 'Diğer önemli bilgiler',
    
    save_draft: 'Taslak Kaydet',
    submit_for_analysis: 'Analize Gönder',
    
    enter_name: 'İsim girin',
    enter_location: 'Konum girin',
    enter_department: 'Departman girin',
    select_option: 'Seçiniz',
    
    // Test Scenarios
    load_test_scenario: 'Test Senaryosu Yükle (Test Amaçlı)',
    clear_form: 'Formu Temizle',
  },
  
  en: {
    // Header
    interactive_mode: 'Interactive Chat',
    batch_mode: 'Batch Analysis',
    
    // Chat Interface
    analysis_steps: 'WORKFLOW STEPS',
    step_1: '1. Incident Received',
    step_1_desc: 'Incident description recorded',
    step_2: '2. Initial Analysis Complete',
    step_2_desc: 'Basic information extracted',
    step_3: '3. Root Cause Analysis',
    step_3_desc: 'Deep analysis in progress',
    step_4: '4. Report Generation',
    step_4_desc: 'Compiling results',
    
    welcome_message: 'Hello! I will help you analyze workplace incidents. Please describe the incident in detail.',
    input_placeholder: 'Type your message...',
    input_hint: 'Enter to send, Shift+Enter for new line',
    reset: 'Reset',
    export: 'Export',
    attach_file: 'Attach File',
    
    analysis_started: 'Analysis started. You will be notified when results are ready.',
    error_occurred: 'An error occurred',
    
    // Questions
    q_fall_protection: 'Was there fall protection on the scaffold?',
    q_safety_harness: 'Was the worker wearing a safety harness?',
    q_safety_training: 'Had the worker received working at height training?',
    q_location: 'Where did the incident occur?',
    q_time: 'When did the incident happen?',
    q_witnesses: 'Are there witnesses to the incident?',
    
    // Options
    yes: 'Yes',
    no: 'No',
    unknown: 'Unknown',
    partial: 'Partial',
    type_answer: 'Type your answer...',
    
    // Incident Form
    incident_report_form: 'Incident Report Form',
    form_subtitle: 'Detailed incident report according to HSG245 standards',
    
    // Sections
    section_reporter: 'Reporter Information',
    section_incident_details: 'Incident Details',
    section_description: 'Incident Description (5W1H)',
    section_safety_equipment: 'Safety Equipment',
    section_witnesses: 'Witnesses',
    section_environment: 'Environmental Conditions',
    section_work_conditions: 'Work Conditions',
    section_injuries: 'Injuries / Damages',
    section_root_cause: 'Root Cause and Corrective Actions',
    
    // Fields
    reported_by: 'Reported by',
    report_date: 'Report Date',
    report_time: 'Report Time',
    incident_date: 'Incident Date',
    incident_time: 'Incident Time',
    location: 'Location',
    department: 'Department',
    event_category: 'Event Category',
    
    incident: 'Incident',
    near_miss: 'Near Miss',
    unsafe_condition: 'Unsafe Condition',
    property_damage: 'Property Damage',
    
    incident_description: 'Incident Description',
    what_where_when_who: 'What, Where, When, Who',
    describe_incident_detail: 'Describe the incident in detail...',
    include_details_hint: 'Please include what, where, when, who, how and why',
    
    what_happened: 'What Happened?',
    where_happened: 'Where Did It Happen?',
    when_happened: 'When Did It Happen?',
    who_involved: 'Who Was Involved?',
    emergency_measures: 'Emergency Measures',
    
    what_placeholder: 'Describe the event',
    where_placeholder: 'Exact location and work area',
    when_placeholder: 'Date, time and shift',
    who_placeholder: 'People involved and their roles',
    emergency_placeholder: 'Measures taken after the incident',
    
    fall_protection_present: 'Was Fall Protection Present?',
    safety_harness_worn: 'Was Safety Harness Worn?',
    safety_training_received: 'Was Safety Training Received?',
    ppe_used: 'PPE Used',
    ppe_placeholder: 'Hard hat, gloves, boots etc.',
    
    witnesses_present: 'Were Witnesses Present?',
    witness_names: 'Witness Names',
    witness_statements: 'Witness Statements',
    witness_names_placeholder: 'Name, role and contact',
    witness_statements_placeholder: 'Witness observations',
    
    weather_conditions: 'Weather Conditions',
    lighting_conditions: 'Lighting',
    noise_level: 'Noise Level',
    temperature: 'Temperature',
    
    weather_placeholder: 'Sunny, rainy, windy etc.',
    lighting_placeholder: 'Good, poor, adequate etc.',
    noise_placeholder: 'High, normal, low',
    temperature_placeholder: 'Degrees (°C)',
    
    work_type: 'Work Type',
    work_height: 'Work Height',
    experience_level: 'Experience Level',
    shift_time: 'Shift',
    work_duration: 'Work Duration',
    
    work_type_placeholder: 'Assembly, maintenance, transport etc.',
    work_height_placeholder: 'In meters',
    experience_placeholder: 'In years',
    shift_placeholder: 'Morning, afternoon, night',
    
    injury_type: 'Injury Type',
    injury_severity: 'Injury Severity',
    body_part: 'Body Part Injured',
    medical_treatment: 'Medical Treatment',
    property_damage: 'Property Damage',
    
    injury_type_placeholder: 'Cut, fracture, bruise etc.',
    body_part_placeholder: 'Head, arm, leg etc.',
    medical_placeholder: 'First aid, hospital etc.',
    
    minor: 'Minor',
    moderate: 'Moderate',
    severe: 'Severe',
    fatal: 'Fatal',
    
    root_cause_initial: 'Root Cause (Initial Assessment)',
    corrective_actions: 'Corrective Actions',
    additional_notes: 'Additional Notes',
    
    root_cause_placeholder: 'What are the root causes?',
    corrective_placeholder: 'Recommended preventive measures',
    notes_placeholder: 'Other important information',
    
    save_draft: 'Save Draft',
    submit_for_analysis: 'Submit for Analysis',
    
    enter_name: 'Enter name',
    enter_location: 'Enter location',
    enter_department: 'Enter department',
    select_option: 'Select',
    
    // Test Scenarios
    load_test_scenario: 'Load Test Scenario (Testing Purpose)',
    clear_form: 'Clear Form',
  },
  
  de: {
    // Header
    interactive_mode: 'Interaktiver Chat',
    batch_mode: 'Stapelanalyse',
    
    // Chat Interface
    analysis_steps: 'WORKFLOW-SCHRITTE',
    step_1: '1. Vorfall Empfangen',
    step_1_desc: 'Vorfallbeschreibung aufgezeichnet',
    step_2: '2. Erstanalyse Abgeschlossen',
    step_2_desc: 'Grundinformationen extrahiert',
    step_3: '3. Ursachenanalyse',
    step_3_desc: 'Tiefenanalyse läuft',
    step_4: '4. Berichterstellung',
    step_4_desc: 'Ergebnisse werden zusammengestellt',
    
    welcome_message: '👋 Hallo! Ich helfe Ihnen bei der Analyse von Arbeitsunfällen. Bitte beschreiben Sie den Vorfall detailliert.',
    input_placeholder: 'Ihre Nachricht...',
    input_hint: 'Enter zum Senden, Shift+Enter für neue Zeile',
    reset: 'Zurücksetzen',
    export: 'Exportieren',
    attach_file: 'Datei Anhängen',
    
    analysis_started: '✅ Analyse gestartet. Sie werden benachrichtigt, wenn die Ergebnisse vorliegen.',
    error_occurred: '❌ Ein Fehler ist aufgetreten',
    
    // Questions
    q_fall_protection: 'Gab es einen Absturzsicherung am Gerüst?',
    q_safety_harness: 'Trug der Arbeiter einen Sicherheitsgurt?',
    q_safety_training: 'Hatte der Arbeiter eine Höhenarbeitstraining erhalten?',
    q_location: 'Wo ereignete sich der Vorfall?',
    q_time: 'Wann geschah der Vorfall?',
    q_witnesses: 'Gibt es Zeugen des Vorfalls?',
    
    // Options
    yes: 'Ja',
    no: 'Nein',
    unknown: 'Unbekannt',
    partial: 'Teilweise',
    type_answer: 'Ihre Antwort eingeben...',
    
    // Test Scenarios
    load_test_scenario: 'Testszenario Laden (Testzweck)',
    clear_form: 'Formular Löschen',
  },
  
  fr: {
    // Header
    interactive_mode: 'Chat Interactif',
    batch_mode: 'Analyse par Lots',
    
    // Chat Interface
    analysis_steps: 'ÉTAPES DU FLUX',
    step_1: '1. Incident Reçu',
    step_1_desc: 'Description de l\'incident enregistrée',
    step_2: '2. Analyse Initiale Terminée',
    step_2_desc: 'Informations de base extraites',
    step_3: '3. Analyse des Causes',
    step_3_desc: 'Analyse approfondie en cours',
    step_4: '4. Génération du Rapport',
    step_4_desc: 'Compilation des résultats',
    
    welcome_message: '👋 Bonjour! Je vais vous aider à analyser les accidents du travail. Veuillez décrire l\'incident en détail.',
    input_placeholder: 'Tapez votre message...',
    input_hint: 'Enter pour envoyer, Shift+Enter pour nouvelle ligne',
    reset: 'Réinitialiser',
    export: 'Exporter',
    attach_file: 'Joindre un Fichier',
    
    analysis_started: '✅ Analyse démarrée. Vous serez informé lorsque les résultats seront prêts.',
    error_occurred: '❌ Une erreur s\'est produite',
    
    // Questions
    q_fall_protection: 'Y avait-il une protection contre les chutes sur l\'échafaudage?',
    q_safety_harness: 'Le travailleur portait-il un harnais de sécurité?',
    q_safety_training: 'Le travailleur avait-il reçu une formation sur le travail en hauteur?',
    q_location: 'Où l\'incident s\'est-il produit?',
    q_time: 'Quand l\'incident s\'est-il produit?',
    q_witnesses: 'Y a-t-il des témoins de l\'incident?',
    
    // Options
    yes: 'Oui',
    no: 'Non',
    unknown: 'Inconnu',
    partial: 'Partiel',
    type_answer: 'Tapez votre réponse...',
    
    // Test Scenarios
    load_test_scenario: 'Charger Scénario de Test (Test)',
    clear_form: 'Effacer Formulaire',
  },
  
  es: {
    // Header
    interactive_mode: 'Chat Interactivo',
    batch_mode: 'Análisis por Lotes',
    
    // Chat Interface
    analysis_steps: 'PASOS DEL FLUJO',
    step_1: '1. Incidente Recibido',
    step_1_desc: 'Descripción del incidente registrada',
    step_2: '2. Análisis Inicial Completo',
    step_2_desc: 'Información básica extraída',
    step_3: '3. Análisis de Causa Raíz',
    step_3_desc: 'Análisis profundo en progreso',
    step_4: '4. Generación de Informe',
    step_4_desc: 'Compilando resultados',
    
    welcome_message: '👋 ¡Hola! Te ayudaré a analizar incidentes laborales. Por favor describe el incidente en detalle.',
    input_placeholder: 'Escribe tu mensaje...',
    input_hint: 'Enter para enviar, Shift+Enter para nueva línea',
    reset: 'Reiniciar',
    export: 'Exportar',
    attach_file: 'Adjuntar Archivo',
    
    analysis_started: '✅ Análisis iniciado. Se le notificará cuando los resultados estén listos.',
    error_occurred: '❌ Ocurrió un error',
    
    // Questions
    q_fall_protection: '¿Había protección contra caídas en el andamio?',
    q_safety_harness: '¿El trabajador llevaba arnés de seguridad?',
    q_safety_training: '¿El trabajador había recibido capacitación para trabajo en altura?',
    q_location: '¿Dónde ocurrió el incidente?',
    q_time: '¿Cuándo ocurrió el incidente?',
    q_witnesses: '¿Hay testigos del incidente?',
    
    // Options
    yes: 'Sí',
    no: 'No',
    unknown: 'Desconocido',
    partial: 'Parcial',
    type_answer: 'Escribe tu respuesta...',
    
    // Test Scenarios
    load_test_scenario: 'Cargar Escenario de Prueba (Propósito de Prueba)',
    clear_form: 'Limpiar Formulario',
  },
  
  ar: {
    // Header
    interactive_mode: 'دردشة تفاعلية',
    batch_mode: 'تحليل دفعي',
    
    // Chat Interface
    analysis_steps: 'خطوات سير العمل',
    step_1: '1. تم استلام الحادث',
    step_1_desc: 'تم تسجيل وصف الحادث',
    step_2: '2. اكتمل التحليل الأولي',
    step_2_desc: 'تم استخراج المعلومات الأساسية',
    step_3: '3. تحليل السبب الجذري',
    step_3_desc: 'التحليل العميق قيد التقدم',
    step_4: '4. إنشاء التقرير',
    step_4_desc: 'جمع النتائج',
    
    welcome_message: '👋 مرحبا! سأساعدك في تحليل حوادث العمل. يرجى وصف الحادث بالتفصيل.',
    input_placeholder: 'اكتب رسالتك...',
    input_hint: 'Enter للإرسال، Shift+Enter لسطر جديد',
    reset: 'إعادة تعيين',
    export: 'تصدير',
    attach_file: 'إرفاق ملف',
    
    analysis_started: '✅ بدأ التحليل. سيتم إعلامك عندما تكون النتائج جاهزة.',
    error_occurred: '❌ حدث خطأ',
    
    // Questions
    q_fall_protection: 'هل كانت هناك حماية من السقوط على السقالة؟',
    q_safety_harness: 'هل كان العامل يرتدي حزام الأمان؟',
    q_safety_training: 'هل تلقى العامل تدريبًا على العمل على الارتفاعات؟',
    q_location: 'أين وقع الحادث؟',
    q_time: 'متى وقع الحادث؟',
    q_witnesses: 'هل هناك شهود على الحادث؟',
    
    // Options
    yes: 'نعم',
    no: 'لا',
    unknown: 'غير معروف',
    partial: 'جزئي',
    type_answer: 'اكتب إجابتك...',
    
    // Test Scenarios
    load_test_scenario: 'تحميل سيناريو الاختبار (الغرض من الاختبار)',
    clear_form: 'مسح النموذج',
  },
};

export const getTranslation = (language, key) => {
  return translations[language]?.[key] || translations.en[key] || key;
};

export const getAllTranslations = (language) => {
  return translations[language] || translations.en;
};

export default translations;

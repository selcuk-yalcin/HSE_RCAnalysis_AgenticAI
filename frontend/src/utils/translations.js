const translations = {
  tr: {
    // Header & Navigation
    interactive_mode: 'Etkileşimli Sohbet',
    batch_mode: 'Toplu Analiz',
    smart_form_v2: 'Akıllı Form (V2)',
    manual_form: 'Manuel Form',
    interactive_analysis: 'Etkileşimli Analiz',
    root_cause_analysis: 'Root Cause Analysis',
    subtitle: 'HSG245 v2.0 - İş Kazası Kök Neden Analiz Sistemi',
    
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
    
    // Report Content Hint
    report_content_hint_title: 'Lütfen belirtin:',
    report_content_hint_body: 'Ne oldu? Nerede oldu? Ne zaman oldu? Kimler dahil oldu? Olay sırasını net şekilde açıklayın.',
    
    // Test Scenarios
    load_test_scenario: 'Test Senaryosu Yükle (Test Amaçlı)',
    clear_form: 'Formu Temizle',
    
    // Weather Options
    weather_sunny: 'Güneşli',
    weather_cloudy: 'Bulutlu',
    weather_rainy: 'Yağmurlu',
    weather_snowy: 'Karlı',
    weather_windy: 'Rüzgarlı',
    weather_foggy: 'Sisli',
    weather_stormy: 'Fırtınalı',
    
    // Lighting Options
    lighting_excellent: 'Mükemmel',
    lighting_good: 'İyi',
    lighting_adequate: 'Yeterli',
    lighting_poor: 'Zayıf',
    lighting_very_poor: 'Çok Zayıf',
    
    // Noise Level Options
    noise_quiet: 'Sessiz - 50 dB altı',
    noise_normal: 'Normal - 50-70 dB',
    noise_loud: 'Yüksek - 70-85 dB',
    noise_very_loud: 'Çok Yüksek - 85 dB üstü',
    
    // Temperature Options
    temp_very_cold: 'Çok Soğuk - 0°C altı',
    temp_cold: 'Soğuk - 0-10°C',
    temp_cool: 'Serin - 10-15°C',
    temp_comfortable: 'Rahat - 15-25°C',
    temp_warm: 'Sıcak - 25-35°C',
    temp_hot: 'Çok Sıcak - 35°C üstü',
    
    // Work Type Options
    work_manual_labor: 'Elle İşçilik',
    work_machine_operation: 'Makine Operasyon',
    work_assembly: 'Montaj',
    work_construction: 'İnşaat',
    work_maintenance: 'Bakım/Onarım',
    work_cleaning: 'Temizlik',
    work_driving: 'Araç Kullanma',
    work_admin: 'İdari İş',
    work_other: 'Diğer',
    
    // Work Height Options
    height_ground_level: 'Yer Seviyesi (0 m)',
    height_low: 'Düşük Yükseklik (1-2 m)',
    height_medium: 'Orta Yükseklik (2-5 m)',
    height_high: 'Yüksek (5-10 m)',
    height_very_high: 'Çok Yüksek (10 m üstü)',
    height_confined_space: 'Kapalı Alan',
    
    // Experience Level Options
    exp_new_employee: 'Yeni Çalışan (1 ay altı)',
    exp_trainee: 'Stajyer/Eğitimdeki (1-3 ay)',
    exp_junior: 'Acemi (3-6 ay)',
    exp_experienced: 'Tecrübeli (6-12 ay)',
    exp_senior: 'Kıdemli (1-5 yıl)',
    exp_expert: 'Uzman (5 yıl üstü)',
    
    // Shift Time Options
    shift_morning: 'Sabah Vardiyası (06:00-14:00)',
    shift_afternoon: 'Öğle Vardiyası (14:00-22:00)',
    shift_night: 'Gece Vardiyası (22:00-06:00)',
    shift_early_morning: 'Erken Sabah (04:00-12:00)',
    shift_late_evening: 'Geç Akşam (20:00-04:00)',
    shift_overtime: 'Fazla Mesai',
    shift_not_applicable: 'N/A Uygulanmaz',
    
    // Smart Questionnaire V2
    smart_questionnaire: 'Akıllı Soru Formu',
    general_questions: 'Genel Sorular',
    detailed_analysis: 'Detaylı Analiz',
    light_mode: 'Açık Tema',
    dark_mode: 'Koyu Tema',
    progress: 'İlerleme',
    questions_answered: 'Cevaplanan Sorular',
    complete_form: 'Formu Tamamla',
    
    // General Questions
    incident_summary: 'Olayın Özeti Nedir?',
    incident_summary_desc: 'Ne oldu, nerede, ne zaman, kim etkilendi?',
    incident_summary_placeholder: 'Kısaca olayı özetleyin...',
    
    incident_when: 'Olay Ne Zaman Gerçekleşti?',
    incident_when_desc: 'Tarih ve saat?',
    
    incident_where: 'Olay Nerede Gerçekleşti?',
    incident_where_desc: 'Tesis, bölüm, spesifik yer',
    incident_where_placeholder: 'Üretim hattı A, Depo 3, vb.',
    
    affected_personnel: 'Etkilenen Personel Bilgileri',
    affected_personnel_desc: 'Ad, ünvan, deneyim',
    affected_personnel_placeholder: 'Ahmet Çelik - Operatör - 2 yıl',
    
    incident_type: 'Olayın Türü Nedir?',
    incident_type_work_accident: 'İş Kazası',
    incident_type_near_miss: 'Ramak Kala (Near Miss)',
    incident_type_environmental: 'Çevre Olayı',
    incident_type_property: 'Mülkiyet Hasarı',
    incident_type_other: 'Diğer',
    
    injury_severity_level: 'Yaralanma/Hasar Şiddeti',
    injury_first_aid: 'İlk Yardım (Hafif)',
    injury_medical: 'Tedavi Gerektiren (Orta)',
    injury_lost_time: 'İş Kaybı (Ciddi)',
    injury_permanent: 'Kalıcı Hasar',
    injury_fatal: 'Ölümlü',
    
    equipment_machinery: 'Kullanılan Ekipman/Makine',
    equipment_machinery_placeholder: 'Forklift, vinç, takım tezgahı vb.',
    
    category_basic: 'Temel',
    category_location: 'Konum',
    category_personnel: 'Personel',
    category_classification: 'Sınıflandırma',
    category_severity: 'Şiddet',
    category_equipment: 'Ekipman',
    category_system: 'Sistem',
    category_management: 'Yönetim',
    category_protection: 'Koruma',
    category_communication: 'İletişim',
    category_response: 'Müdahale',
    category_other: 'Diğer',
    
    // Questionnaire Questions
    procedure_available: 'Prosedür/İş Talimatı Var Mıydı?',
    procedure_no: 'Hayır, yoktu',
    procedure_unknown: 'Vardı ama bilinmiyordu',
    procedure_known: 'Vardı ve biliniyordu',
    procedure_not_followed: 'Vardı ama uygulanmıyordu',
    
    training_provided: 'Eğitim Verilmiş Miydi?',
    training_no: 'Hayır',
    training_general: 'Genel eğitim var ama spesifik yoktu',
    training_specific: 'Evet, spesifik eğitim vardı',
    
    risk_assessment: 'Risk Değerlendirmesi Yapılmış Mıydı?',
    risk_no: 'Hayır',
    risk_not_applied: 'Yapıldı ama kontroller uygulanmadı',
    risk_applied: 'Yapıldı ve kontroller takip edildi',
    
    supervision: 'Denetim/Gözetim Var Mıydı?',
    supervision_no: 'Hayır',
    supervision_partial: 'Kısmen',
    supervision_full: 'Evet, tam denetim vardı',
    
    ppe_adequate: 'KKD (Kişisel Koruyucu Donanım) Yeterli Miydi?',
    ppe_not_needed: 'Gerekli değildi',
    ppe_not_provided: 'Gerekli ama sağlanmadı',
    ppe_not_used: 'Sağlandı ama kullanılmadı',
    ppe_used: 'Sağlandı ve kullanıldı',
    
    communication_issue: 'İletişim Sorun Var Mıydı?',
    communication_major: 'Evet, önemli iletişim kopukluğu',
    communication_unclear: 'Kısmen, talimatlar açık değildi',
    communication_clear: 'Hayır, iletişim açıktı',
    
    similar_incident: 'Benzer Olay Daha Önce Yaşandı Mı?',
    similar_yes: 'Evet, benzer olaylar yaşandı',
    similar_near_miss: 'Ramak kala (near miss) var',
    similar_first: 'Hayır, bu ilk',
    
    emergency_response: 'Acil Müdahale/İlk Yardım Yeterli Miydi?',
    emergency_inadequate: 'Hayır, yetersizdi',
    emergency_partial: 'Kısmen yapıldı',
    emergency_professional: 'Evet, profesyonel müdahale yapıldı',
    
    additional_comments: 'Ek Açıklamalar',
    additional_comments_desc: 'Önemli detaylar, tanık ifadeleri, vb.',
    additional_comments_placeholder: 'Başka dikkat çeken noktalar...',
    
    select_placeholder: '-- Seçiniz --',
    smart_investigation_system: 'Akıllı Soruşturma Sistemi',
    systematic_info_collection: 'Olay hakkında sistemli bilgi toplayarak kök nedene ulaşın',
    auto_detected_codes: 'Otomatik Tespit Edilen Kodlar',
    no_detailed_sections: 'Henüz detaylı analiz bölümü yok.',
    enter_more_info: 'Genel sorularda daha fazla bilgi girerek detaylı seçenekler görün.',
    reset_form: 'Sıfırla',
    complete_investigation: 'Soruşturmayı Tamamla',
  },
  
  en: {
    // Header & Navigation
    interactive_mode: 'Interactive Chat',
    batch_mode: 'Batch Analysis',
    smart_form_v2: 'Smart Form (V2)',
    manual_form: 'Manual Form',
    interactive_analysis: 'Interactive Analysis',
    root_cause_analysis: 'Root Cause Analysis',
    subtitle: 'HSG245 v2.0 - Workplace Incident Root Cause Analysis System',
    
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
    
    // Report Content Hint
    report_content_hint_title: 'Please include:',
    report_content_hint_body: 'What happened? Where did it happen? When did it happen? Who was involved? Describe the sequence of events clearly.',
    
    // Weather Options
    weather_sunny: 'Sunny',
    weather_cloudy: 'Cloudy',
    weather_rainy: 'Rainy',
    weather_snowy: 'Snowy',
    weather_windy: 'Windy',
    weather_foggy: 'Foggy',
    weather_stormy: 'Stormy',
    
    // Lighting Options
    lighting_excellent: 'Excellent',
    lighting_good: 'Good',
    lighting_adequate: 'Adequate',
    lighting_poor: 'Poor',
    lighting_very_poor: 'Very Poor',
    
    // Noise Level Options
    noise_quiet: 'Quiet - Below 50 dB',
    noise_normal: 'Normal - 50-70 dB',
    noise_loud: 'Loud - 70-85 dB',
    noise_very_loud: 'Very Loud - Above 85 dB',
    
    // Temperature Options
    temp_very_cold: 'Very Cold - Below 0°C',
    temp_cold: 'Cold - 0-10°C',
    temp_cool: 'Cool - 10-15°C',
    temp_comfortable: 'Comfortable - 15-25°C',
    temp_warm: 'Warm - 25-35°C',
    temp_hot: 'Very Hot - Above 35°C',
    
    // Work Type Options
    work_manual_labor: 'Manual Labor',
    work_machine_operation: 'Machine Operation',
    work_assembly: 'Assembly',
    work_construction: 'Construction',
    work_maintenance: 'Maintenance/Repair',
    work_cleaning: 'Cleaning',
    work_driving: 'Vehicle Operation',
    work_admin: 'Administrative Work',
    work_other: 'Other',
    
    // Work Height Options
    height_ground_level: 'Ground Level (0 m)',
    height_low: 'Low Height (1-2 m)',
    height_medium: 'Medium Height (2-5 m)',
    height_high: 'High (5-10 m)',
    height_very_high: 'Very High (Above 10 m)',
    height_confined_space: 'Confined Space',
    
    // Experience Level Options
    exp_new_employee: 'New Employee (Less than 1 month)',
    exp_trainee: 'Trainee/In Training (1-3 months)',
    exp_junior: 'Junior (3-6 months)',
    exp_experienced: 'Experienced (6-12 months)',
    exp_senior: 'Senior (1-5 years)',
    exp_expert: 'Expert (More than 5 years)',
    
    // Shift Time Options
    shift_morning: 'Morning Shift (06:00-14:00)',
    shift_afternoon: 'Afternoon Shift (14:00-22:00)',
    shift_night: 'Night Shift (22:00-06:00)',
    shift_early_morning: 'Early Morning (04:00-12:00)',
    shift_late_evening: 'Late Evening (20:00-04:00)',
    shift_overtime: 'Overtime',
    shift_not_applicable: 'N/A Not Applicable',
    
    // Test Scenarios
    load_test_scenario: 'Load Test Scenario (Testing Purpose)',
    clear_form: 'Clear Form',
    
    // Smart Questionnaire V2
    smart_questionnaire: 'Smart Questionnaire',
    general_questions: 'General Questions',
    detailed_analysis: 'Detailed Analysis',
    light_mode: 'Light Mode',
    dark_mode: 'Dark Mode',
    progress: 'Progress',
    questions_answered: 'Questions Answered',
    complete_form: 'Complete Form',
    
    // General Questions
    incident_summary: 'What is the Incident Summary?',
    incident_summary_desc: 'What happened, where, when, who was affected?',
    incident_summary_placeholder: 'Briefly summarize the incident...',
    
    incident_when: 'When Did the Incident Occur?',
    incident_when_desc: 'Date and time?',
    
    incident_where: 'Where Did the Incident Occur?',
    incident_where_desc: 'Facility, department, specific location',
    incident_where_placeholder: 'Production line A, Warehouse 3, etc.',
    
    affected_personnel: 'Affected Personnel Information',
    affected_personnel_desc: 'Name, title, experience',
    affected_personnel_placeholder: 'John Smith - Operator - 2 years',
    
    incident_type: 'What is the Incident Type?',
    incident_type_work_accident: 'Work Accident',
    incident_type_near_miss: 'Near Miss',
    incident_type_environmental: 'Environmental Incident',
    incident_type_property: 'Property Damage',
    incident_type_other: 'Other',
    
    injury_severity_level: 'Injury/Damage Severity',
    injury_first_aid: 'First Aid (Minor)',
    injury_medical: 'Medical Treatment Required (Moderate)',
    injury_lost_time: 'Lost Time Injury (Serious)',
    injury_permanent: 'Permanent Disability',
    injury_fatal: 'Fatal',
    
    equipment_machinery: 'Equipment/Machinery Used',
    equipment_machinery_placeholder: 'Forklift, crane, machine tool, etc.',
    
    category_basic: 'Basic',
    category_location: 'Location',
    category_personnel: 'Personnel',
    category_classification: 'Classification',
    category_severity: 'Severity',
    category_equipment: 'Equipment',
    category_system: 'System',
    category_management: 'Management',
    category_protection: 'Protection',
    category_communication: 'Communication',
    category_response: 'Response',
    category_other: 'Other',
    
    // Questionnaire Questions
    procedure_available: 'Was Procedure/Work Instruction Available?',
    procedure_no: 'No, it did not exist',
    procedure_unknown: 'Existed but was unknown',
    procedure_known: 'Existed and was known',
    procedure_not_followed: 'Existed but not followed',
    
    training_provided: 'Was Training Provided?',
    training_no: 'No',
    training_general: 'General training but no specific',
    training_specific: 'Yes, specific training provided',
    
    risk_assessment: 'Was Risk Assessment Done?',
    risk_no: 'No',
    risk_not_applied: 'Done but controls not applied',
    risk_applied: 'Done and controls monitored',
    
    supervision: 'Was Supervision Present?',
    supervision_no: 'No',
    supervision_partial: 'Partial',
    supervision_full: 'Yes, full supervision',
    
    ppe_adequate: 'Was PPE (Personal Protective Equipment) Adequate?',
    ppe_not_needed: 'Not required',
    ppe_not_provided: 'Required but not provided',
    ppe_not_used: 'Provided but not used',
    ppe_used: 'Provided and used',
    
    communication_issue: 'Was There a Communication Issue?',
    communication_major: 'Yes, major communication breakdown',
    communication_unclear: 'Partially, instructions unclear',
    communication_clear: 'No, communication was clear',
    
    similar_incident: 'Has Similar Incident Occurred Before?',
    similar_yes: 'Yes, similar incidents occurred',
    similar_near_miss: 'Near miss exists',
    similar_first: 'No, this is the first',
    
    emergency_response: 'Was Emergency Response/First Aid Adequate?',
    emergency_inadequate: 'No, inadequate',
    emergency_partial: 'Partially done',
    emergency_professional: 'Yes, professional response',
    
    additional_comments: 'Additional Comments',
    additional_comments_desc: 'Important details, witness statements, etc.',
    additional_comments_placeholder: 'Other notable points...',
    
    select_placeholder: '-- Select --',
    smart_investigation_system: 'Smart Investigation System',
    systematic_info_collection: 'Reach root cause by collecting information systematically',
    auto_detected_codes: 'Automatically Detected Codes',
    no_detailed_sections: 'No detailed analysis sections yet.',
    enter_more_info: 'Enter more information in general questions to see detailed options.',
    reset_form: 'Reset',
    complete_investigation: 'Complete Investigation',
  },
  
  de: {
    // Header & Navigation
    interactive_mode: 'Interaktiver Chat',
    batch_mode: 'Stapelanalyse',
    smart_form_v2: 'Intelligentes Formular (V2)',
    manual_form: 'Manuelles Formular',
    interactive_analysis: 'Interaktive Analyse',
    root_cause_analysis: 'Ursachenanalyse',
    subtitle: 'HSG245 v2.0 - Arbeitsunfall-Ursachenanalysesystem',
    
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
    
    // Sections
    section_reporter: 'Reporter-Informationen',
    section_incident_details: 'Vorfalldetails',
    section_description: 'Vorfallbeschreibung (5W1H)',
    section_safety_equipment: 'Sicherheitsausrüstung',
    section_witnesses: 'Zeugen',
    section_environment: 'Umweltbedingungen',
    section_work_conditions: 'Arbeitsbedingungen',
    section_injuries: 'Verletzungen / Schäden',
    section_root_cause: 'Grundursache und Korrekturmaßnahmen',
    
    // Incident Form - Main Fields
    reported_by: 'Berichterstattet von',
    report_date: 'Berichtsdatum',
    report_time: 'Berichtszeit',
    incident_date: 'Vorfallsdatum',
    incident_time: 'Vorfallszeit',
    location: 'Ort',
    department: 'Abteilung',
    event_category: 'Ereigniskategorie',
    
    incident: 'Unfall',
    near_miss: 'Beinahe-Unfall',
    unsafe_condition: 'Unsicherer Zustand',
    property_damage: 'Sachschaden',
    
    incident_description: 'Vorfallbeschreibung',
    what_where_when_who: 'Was, Wo, Wann, Wer',
    describe_incident_detail: 'Beschreiben Sie den Unfall detailliert...',
    
    fall_protection_present: 'Gab es einen Absturzsicherung?',
    safety_harness_worn: 'Trug der Arbeiter einen Sicherheitsgurt?',
    safety_training_received: 'Hatte der Arbeiter Sicherheitstraining erhalten?',
    ppe_used: 'Verwendete PSA',
    ppe_placeholder: 'Helm, Handschuhe, Schuhe usw.',
    
    witnesses_present: 'Waren Zeugen anwesend?',
    witness_names: 'Namen der Zeugen',
    witness_statements: 'Aussagen der Zeugen',
    witness_names_placeholder: 'Name, Position und Kontakt',
    witness_statements_placeholder: 'Beobachtungen der Zeugen',
    
    weather_conditions: 'Wetterbedingungen',
    lighting_conditions: 'Lichtverhältnisse',
    noise_level: 'Lärmpegel',
    temperature: 'Temperatur',
    
    weather_placeholder: 'Sonnig, regnerisch, windig usw.',
    lighting_placeholder: 'Gut, schlecht, angemessen usw.',
    noise_placeholder: 'Hoch, normal, niedrig',
    temperature_placeholder: 'Grad (°C)',
    
    work_type: 'Arbeitstyp',
    work_height: 'Arbeitshöhe',
    experience_level: 'Erfahrungsstufe',
    shift_time: 'Schicht',
    work_duration: 'Arbeitsdauer',
    
    work_type_placeholder: 'Montage, Wartung, Transport usw.',
    work_height_placeholder: 'In Metern',
    experience_placeholder: 'In Jahren',
    shift_placeholder: 'Morgen, Nachmittag, Nacht',
    
    // Report Content Hint
    report_content_hint_title: 'Bitte geben Sie an:',
    report_content_hint_body: 'Was ist passiert? Wo ist es passiert? Wann ist es passiert? Wer war beteiligt? Beschreiben Sie den Ablauf des Ereignisses klar.',
    
    // Weather Options
    weather_sunny: 'Sonnig',
    weather_cloudy: 'Bewölkt',
    weather_rainy: 'Regnerisch',
    weather_snowy: 'Schneereich',
    weather_windy: 'Windig',
    weather_foggy: 'Neblig',
    weather_stormy: 'Stürmisch',
    
    // Lighting Options
    lighting_excellent: 'Ausgezeichnet',
    lighting_good: 'Gut',
    lighting_adequate: 'Angemessen',
    lighting_poor: 'Schlecht',
    lighting_very_poor: 'Sehr schlecht',
    
    // Noise Level Options
    noise_quiet: 'Ruhig - unter 50 dB',
    noise_normal: 'Normal - 50-70 dB',
    noise_loud: 'Laut - 70-85 dB',
    noise_very_loud: 'Sehr laut - über 85 dB',
    
    // Temperature Options
    temp_very_cold: 'Sehr kalt - unter 0°C',
    temp_cold: 'Kalt - 0-10°C',
    temp_cool: 'Kühl - 10-15°C',
    temp_comfortable: 'Komfortabel - 15-25°C',
    temp_warm: 'Warm - 25-35°C',
    temp_hot: 'Sehr heiß - über 35°C',
    
    // Work Type Options
    work_manual_labor: 'Manuelle Arbeit',
    work_machine_operation: 'Maschinenoperation',
    work_assembly: 'Montage',
    work_construction: 'Konstruktion',
    work_maintenance: 'Wartung/Reparatur',
    work_cleaning: 'Reinigung',
    work_driving: 'Fahrzeugbetrieb',
    work_admin: 'Verwaltungsarbeit',
    work_other: 'Sonstige',
    
    // Work Height Options
    height_ground_level: 'Bodenniveau (0 m)',
    height_low: 'Niedrige Höhe (1-2 m)',
    height_medium: 'Mittlere Höhe (2-5 m)',
    height_high: 'Hoch (5-10 m)',
    height_very_high: 'Sehr hoch (über 10 m)',
    height_confined_space: 'Beengter Raum',
    
    // Experience Level Options
    exp_new_employee: 'Neuer Mitarbeiter (weniger als 1 Monat)',
    exp_trainee: 'Auszubildender/In Schulung (1-3 Monate)',
    exp_junior: 'Junior (3-6 Monate)',
    exp_experienced: 'Erfahren (6-12 Monate)',
    exp_senior: 'Senior (1-5 Jahre)',
    exp_expert: 'Experte (über 5 Jahre)',
    
    // Shift Time Options
    shift_morning: 'Frühschicht (06:00-14:00)',
    shift_afternoon: 'Spätschicht (14:00-22:00)',
    shift_night: 'Nachtschicht (22:00-06:00)',
    shift_early_morning: 'Früher Morgen (04:00-12:00)',
    shift_late_evening: 'Später Abend (20:00-04:00)',
    shift_overtime: 'Überstunden',
    shift_not_applicable: 'N/A Nicht anwendbar',
    
    // Injury/Damages Section
    injury_type: 'Verletzungstyp',
    injury_severity: 'Verletzungsschweregrad',
    body_part: 'Verletzte Körperstelle',
    medical_treatment: 'Medizinische Behandlung',
    property_damage: 'Sachschaden',
    
    injury_type_placeholder: 'Schnitt, Bruch, Quetschung usw.',
    body_part_placeholder: 'Kopf, Arm, Bein usw.',
    medical_placeholder: 'Erste Hilfe, Krankenhaus usw.',
    
    root_cause_initial: 'Grundursache (Erste Bewertung)',
    corrective_actions: 'Korrekturmaßnahmen',
    additional_notes: 'Zusätzliche Notizen',
    
    root_cause_placeholder: 'Was sind die Grundursachen?',
    corrective_placeholder: 'Empfohlene Vorbeugungsmaßnahmen',
    notes_placeholder: 'Weitere wichtige Informationen',
    
    // Emergency & Buttons
    emergency_measures: 'Notfallmaßnahmen',
    save_draft: 'Entwurf Speichern',
    submit_for_analysis: 'Zur Analyse Einreichen',
    
    // Test Scenarios
    load_test_scenario: 'Testszenario Laden (Testzweck)',
    clear_form: 'Formular Löschen',
  },
  
  fr: {
    // Header & Navigation
    interactive_mode: 'Chat Interactif',
    batch_mode: 'Analyse par Lots',
    smart_form_v2: 'Formulaire Intelligent (V2)',
    manual_form: 'Formulaire Manuel',
    interactive_analysis: 'Analyse Interactive',
    root_cause_analysis: 'Analyse des Causes Racines',
    subtitle: 'HSG245 v2.0 - Système d\'Analyse des Causes d\'Accidents du Travail',
    
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
    
    // Sections
    section_reporter: 'Informations du Déclarant',
    section_incident_details: 'Détails de l\'Incident',
    section_description: 'Description de l\'Incident (5W1H)',
    section_safety_equipment: 'Équipement de Sécurité',
    section_witnesses: 'Témoins',
    section_environment: 'Conditions Environnementales',
    section_work_conditions: 'Conditions de Travail',
    section_injuries: 'Blessures / Dommages',
    section_root_cause: 'Cause Racine et Actions Correctives',
    
    // Incident Form - Main Fields
    reported_by: 'Signalé par',
    report_date: 'Date du Signalement',
    report_time: 'Heure du Signalement',
    incident_date: 'Date de l\'Incident',
    incident_time: 'Heure de l\'Incident',
    location: 'Lieu',
    department: 'Département',
    event_category: 'Catégorie d\'Événement',
    
    incident: 'Incident',
    near_miss: 'Quasi-Accident',
    unsafe_condition: 'Condition Dangereuse',
    property_damage: 'Dommages Matériels',
    
    incident_description: 'Description de l\'Incident',
    what_where_when_who: 'Quoi, Où, Quand, Qui',
    describe_incident_detail: 'Décrivez l\'incident en détail...',
    
    fall_protection_present: 'Y avait-il une protection contre les chutes?',
    safety_harness_worn: 'Le travailleur portait-il un harnais de sécurité?',
    safety_training_received: 'Le travailleur avait-il reçu une formation de sécurité?',
    ppe_used: 'EPI Utilisé',
    ppe_placeholder: 'Casque, gants, chaussures, etc.',
    
    witnesses_present: 'Y avait-il des témoins?',
    witness_names: 'Noms des Témoins',
    witness_statements: 'Déclarations des Témoins',
    witness_names_placeholder: 'Nom, rôle et contact',
    witness_statements_placeholder: 'Observations des témoins',
    
    weather_conditions: 'Conditions Météorologiques',
    lighting_conditions: 'Conditions d\'Éclairage',
    noise_level: 'Niveau de Bruit',
    temperature: 'Température',
    
    weather_placeholder: 'Ensoleillé, pluvieux, venteux, etc.',
    lighting_placeholder: 'Bon, mauvais, adéquat, etc.',
    noise_placeholder: 'Élevé, normal, bas',
    temperature_placeholder: 'Degrés (°C)',
    
    work_type: 'Type de Travail',
    work_height: 'Hauteur de Travail',
    experience_level: 'Niveau d\'Expérience',
    shift_time: 'Quart',
    work_duration: 'Durée du Travail',
    
    work_type_placeholder: 'Assemblage, maintenance, transport, etc.',
    work_height_placeholder: 'En mètres',
    experience_placeholder: 'En années',
    shift_placeholder: 'Matin, après-midi, nuit',
    
    // Report Content Hint
    report_content_hint_title: 'Veuillez préciser :',
    report_content_hint_body: 'Que s\'est-il passé ? Où cela s\'est-il passé ? Quand cela s\'est-il passé ? Qui était impliqué ? Décrivez clairement le déroulement des événements.',
    
    // Weather Options
    weather_sunny: 'Ensoleillé',
    weather_cloudy: 'Nuageux',
    weather_rainy: 'Pluvieux',
    weather_snowy: 'Neigeux',
    weather_windy: 'Venteux',
    weather_foggy: 'Brumeux',
    weather_stormy: 'Orageux',
    
    // Lighting Options
    lighting_excellent: 'Excellent',
    lighting_good: 'Bon',
    lighting_adequate: 'Adéquat',
    lighting_poor: 'Mauvais',
    lighting_very_poor: 'Très mauvais',
    
    // Noise Level Options
    noise_quiet: 'Calme - moins de 50 dB',
    noise_normal: 'Normal - 50-70 dB',
    noise_loud: 'Bruyant - 70-85 dB',
    noise_very_loud: 'Très bruyant - plus de 85 dB',
    
    // Temperature Options
    temp_very_cold: 'Très froid - moins de 0°C',
    temp_cold: 'Froid - 0-10°C',
    temp_cool: 'Frais - 10-15°C',
    temp_comfortable: 'Confortable - 15-25°C',
    temp_warm: 'Chaud - 25-35°C',
    temp_hot: 'Très chaud - plus de 35°C',
    
    // Work Type Options
    work_manual_labor: 'Travail Manuel',
    work_machine_operation: 'Opération Machines',
    work_assembly: 'Montage',
    work_construction: 'Construction',
    work_maintenance: 'Maintenance/Réparation',
    work_cleaning: 'Nettoyage',
    work_driving: 'Opération Véhicule',
    work_admin: 'Travail Administratif',
    work_other: 'Autre',
    
    // Work Height Options
    height_ground_level: 'Niveau du Sol (0 m)',
    height_low: 'Faible Hauteur (1-2 m)',
    height_medium: 'Hauteur Moyenne (2-5 m)',
    height_high: 'Élevé (5-10 m)',
    height_very_high: 'Très Élevé (plus de 10 m)',
    height_confined_space: 'Espace Confiné',
    
    // Experience Level Options
    exp_new_employee: 'Nouvel Employé (moins de 1 mois)',
    exp_trainee: 'Stagiaire/En Formation (1-3 mois)',
    exp_junior: 'Junior (3-6 mois)',
    exp_experienced: 'Expérimenté (6-12 mois)',
    exp_senior: 'Senior (1-5 ans)',
    exp_expert: 'Expert (plus de 5 ans)',
    
    // Shift Time Options
    shift_morning: 'Quart du Matin (06:00-14:00)',
    shift_afternoon: 'Quart de l\'Après-midi (14:00-22:00)',
    shift_night: 'Quart de Nuit (22:00-06:00)',
    shift_early_morning: 'Tôt le Matin (04:00-12:00)',
    shift_late_evening: 'Tard le Soir (20:00-04:00)',
    shift_overtime: 'Heures Supplémentaires',
    shift_not_applicable: 'N/A Non Applicable',
    
    // Injury/Damages Section
    injury_type: 'Type de Blessure',
    injury_severity: 'Gravité de la Blessure',
    body_part: 'Partie du Corps Blessée',
    medical_treatment: 'Traitement Médical',
    property_damage: 'Dommages Matériels',
    
    injury_type_placeholder: 'Coupure, fracture, contusion, etc.',
    body_part_placeholder: 'Tête, bras, jambe, etc.',
    medical_placeholder: 'Premiers secours, hôpital, etc.',
    
    root_cause_initial: 'Cause Racine (Évaluation Initiale)',
    corrective_actions: 'Actions Correctives',
    additional_notes: 'Notes Supplémentaires',
    
    root_cause_placeholder: 'Quelles sont les causes racines?',
    corrective_placeholder: 'Mesures de prévention recommandées',
    notes_placeholder: 'Autres informations importantes',
    
    // Emergency & Buttons
    emergency_measures: 'Mesures d\'Urgence',
    save_draft: 'Enregistrer Brouillon',
    submit_for_analysis: 'Soumettre pour Analyse',
    
    // Test Scenarios
    load_test_scenario: 'Charger Scénario de Test (Test)',
    clear_form: 'Effacer Formulaire',
  },
  
  es: {
    // Header & Navigation
    interactive_mode: 'Chat Interactivo',
    batch_mode: 'Análisis por Lotes',
    smart_form_v2: 'Formulario Inteligente (V2)',
    manual_form: 'Formulario Manual',
    interactive_analysis: 'Análisis Interactivo',
    root_cause_analysis: 'Análisis de Causa Raíz',
    subtitle: 'HSG245 v2.0 - Sistema de Análisis de Causas de Accidentes Laborales',
    
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
    
    welcome_message: ' ¡Hola! Te ayudaré a analizar incidentes laborales. Por favor describe el incidente en detalle.',
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
    
    // Sections
    section_reporter: 'Información del Reportero',
    section_incident_details: 'Detalles del Incidente',
    section_description: 'Descripción del Incidente (5W1H)',
    section_safety_equipment: 'Equipo de Seguridad',
    section_witnesses: 'Testigos',
    section_environment: 'Condiciones Ambientales',
    section_work_conditions: 'Condiciones de Trabajo',
    section_injuries: 'Lesiones / Daños',
    section_root_cause: 'Causa Raíz y Acciones Correctivas',
    
    // Incident Form - Main Fields
    reported_by: 'Reportado por',
    report_date: 'Fecha de Reporte',
    report_time: 'Hora de Reporte',
    incident_date: 'Fecha del Incidente',
    incident_time: 'Hora del Incidente',
    location: 'Ubicación',
    department: 'Departamento',
    event_category: 'Categoría del Evento',
    
    incident: 'Incidente',
    near_miss: 'Casi Accidente',
    unsafe_condition: 'Condición Peligrosa',
    property_damage: 'Daño a Propiedad',
    
    incident_description: 'Descripción del Incidente',
    what_where_when_who: 'Qué, Dónde, Cuándo, Quién',
    describe_incident_detail: 'Describa el incidente en detalle...',
    
    fall_protection_present: '¿Había protección contra caídas?',
    safety_harness_worn: '¿El trabajador llevaba arnés de seguridad?',
    safety_training_received: '¿El trabajador había recibido capacitación de seguridad?',
    ppe_used: 'EPP Utilizado',
    ppe_placeholder: 'Casco, guantes, botas, etc.',
    
    witnesses_present: '¿Había testigos?',
    witness_names: 'Nombres de los Testigos',
    witness_statements: 'Declaraciones de Testigos',
    witness_names_placeholder: 'Nombre, rol y contacto',
    witness_statements_placeholder: 'Observaciones de los testigos',
    
    weather_conditions: 'Condiciones Climáticas',
    lighting_conditions: 'Condiciones de Iluminación',
    noise_level: 'Nivel de Ruido',
    temperature: 'Temperatura',
    
    weather_placeholder: 'Soleado, lluvioso, ventoso, etc.',
    lighting_placeholder: 'Bueno, malo, adecuado, etc.',
    noise_placeholder: 'Alto, normal, bajo',
    temperature_placeholder: 'Grados (°C)',
    
    work_type: 'Tipo de Trabajo',
    work_height: 'Altura de Trabajo',
    experience_level: 'Nivel de Experiencia',
    shift_time: 'Turno',
    work_duration: 'Duración del Trabajo',
    
    work_type_placeholder: 'Ensamblaje, mantenimiento, transporte, etc.',
    work_height_placeholder: 'En metros',
    experience_placeholder: 'En años',
    shift_placeholder: 'Mañana, tarde, noche',
    
    // Report Content Hint
    report_content_hint_title: 'Por favor indique:',
    report_content_hint_body: '¿Qué ocurrió? ¿Dónde ocurrió? ¿Cuándo ocurrió? ¿Quiénes estuvieron involucrados? Describa claramente la secuencia de los hechos.',
    
    // Weather Options
    weather_sunny: 'Soleado',
    weather_cloudy: 'Nublado',
    weather_rainy: 'Lluvioso',
    weather_snowy: 'Nevado',
    weather_windy: 'Ventoso',
    weather_foggy: 'Brumoso',
    weather_stormy: 'Tormentoso',
    
    // Lighting Options
    lighting_excellent: 'Excelente',
    lighting_good: 'Bueno',
    lighting_adequate: 'Adecuado',
    lighting_poor: 'Pobre',
    lighting_very_poor: 'Muy Pobre',
    
    // Noise Level Options
    noise_quiet: 'Silencioso - Menos de 50 dB',
    noise_normal: 'Normal - 50-70 dB',
    noise_loud: 'Ruidoso - 70-85 dB',
    noise_very_loud: 'Muy Ruidoso - Más de 85 dB',
    
    // Temperature Options
    temp_very_cold: 'Muy Frío - Menos de 0°C',
    temp_cold: 'Frío - 0-10°C',
    temp_cool: 'Fresco - 10-15°C',
    temp_comfortable: 'Cómodo - 15-25°C',
    temp_warm: 'Cálido - 25-35°C',
    temp_hot: 'Muy Caliente - Más de 35°C',
    
    // Work Type Options
    work_manual_labor: 'Trabajo Manual',
    work_machine_operation: 'Operación de Máquinas',
    work_assembly: 'Montaje',
    work_construction: 'Construcción',
    work_maintenance: 'Mantenimiento/Reparación',
    work_cleaning: 'Limpieza',
    work_driving: 'Operación de Vehículos',
    work_admin: 'Trabajo Administrativo',
    work_other: 'Otro',
    
    // Work Height Options
    height_ground_level: 'Nivel del Suelo (0 m)',
    height_low: 'Altura Baja (1-2 m)',
    height_medium: 'Altura Media (2-5 m)',
    height_high: 'Alto (5-10 m)',
    height_very_high: 'Muy Alto (Más de 10 m)',
    height_confined_space: 'Espacio Confinado',
    
    // Experience Level Options
    exp_new_employee: 'Empleado Nuevo (Menos de 1 mes)',
    exp_trainee: 'Aprendiz/En Capacitación (1-3 meses)',
    exp_junior: 'Junior (3-6 meses)',
    exp_experienced: 'Experimentado (6-12 meses)',
    exp_senior: 'Senior (1-5 años)',
    exp_expert: 'Experto (Más de 5 años)',
    
    // Shift Time Options
    shift_morning: 'Turno Matutino (06:00-14:00)',
    shift_afternoon: 'Turno Vespertino (14:00-22:00)',
    shift_night: 'Turno Nocturno (22:00-06:00)',
    shift_early_morning: 'Madrugada (04:00-12:00)',
    shift_late_evening: 'Tarde Nocturna (20:00-04:00)',
    shift_overtime: 'Horas Extras',
    shift_not_applicable: 'N/A No Aplica',
    
    // Injury/Damages Section
    injury_type: 'Tipo de Lesión',
    injury_severity: 'Gravedad de la Lesión',
    body_part: 'Parte del Cuerpo Lesionada',
    medical_treatment: 'Tratamiento Médico',
    property_damage: 'Daño a la Propiedad',
    
    injury_type_placeholder: 'Corte, fractura, contusión, etc.',
    body_part_placeholder: 'Cabeza, brazo, pierna, etc.',
    medical_placeholder: 'Primeros auxilios, hospital, etc.',
    
    root_cause_initial: 'Causa Raíz (Evaluación Inicial)',
    corrective_actions: 'Acciones Correctivas',
    additional_notes: 'Notas Adicionales',
    
    root_cause_placeholder: '¿Cuáles son las causas raíz?',
    corrective_placeholder: 'Medidas preventivas recomendadas',
    notes_placeholder: 'Otra información importante',
    
    // Emergency & Buttons
    emergency_measures: 'Medidas de Emergencia',
    save_draft: 'Guardar Borrador',
    submit_for_analysis: 'Enviar para Análisis',
    
    // Test Scenarios
    load_test_scenario: 'Cargar Escenario de Prueba (Propósito de Prueba)',
    clear_form: 'Limpiar Formulario',
  },
  
  ar: {
    // Header & Navigation
    interactive_mode: 'دردشة تفاعلية',
    batch_mode: 'تحليل دفعي',
    smart_form_v2: 'نموذج ذكي (V2)',
    manual_form: 'نموذج يدوي',
    interactive_analysis: 'تحليل تفاعلي',
    root_cause_analysis: 'تحليل السبب الجذري',
    subtitle: 'HSG245 v2.0 - نظام تحليل الأسباب الجذرية لحوادث العمل',
    
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
    
    // Sections
    section_reporter: 'معلومات المبلغ',
    section_incident_details: 'تفاصيل الحادث',
    section_description: 'وصف الحادث (5W1H)',
    section_safety_equipment: 'معدات الأمان',
    section_witnesses: 'الشهود',
    section_environment: 'الظروف البيئية',
    section_work_conditions: 'ظروف العمل',
    section_injuries: 'الإصابات / الأضرار',
    section_root_cause: 'السبب الجذري والإجراءات التصحيحية',
    
    // Incident Form - Main Fields
    reported_by: 'الذي أبلغ عنه',
    report_date: 'تاريخ التقرير',
    report_time: 'وقت التقرير',
    incident_date: 'تاريخ الحادث',
    incident_time: 'وقت الحادث',
    location: 'الموقع',
    department: 'القسم',
    event_category: 'فئة الحدث',
    
    incident: 'حادث',
    near_miss: 'حادث قاب قوسين أو أدنى',
    unsafe_condition: 'حالة غير آمنة',
    property_damage: 'الأضرار المادية',
    
    incident_description: 'وصف الحادث',
    what_where_when_who: 'ماذا، أين، متى، من',
    describe_incident_detail: 'وصف الحادث بالتفصيل...',
    
    fall_protection_present: 'هل كانت هناك حماية من السقوط؟',
    safety_harness_worn: 'هل كان العامل يرتدي حزام الأمان؟',
    safety_training_received: 'هل تلقى العامل تدريب الأمان؟',
    ppe_used: 'معدات الحماية الشخصية المستخدمة',
    ppe_placeholder: 'خوذة، قفازات، أحذية، إلخ.',
    
    witnesses_present: 'هل كان هناك شهود؟',
    witness_names: 'أسماء الشهود',
    witness_statements: 'أقوال الشهود',
    witness_names_placeholder: 'الاسم والدور والتواصل',
    witness_statements_placeholder: 'ملاحظات الشهود',
    
    weather_conditions: 'الظروف الجوية',
    lighting_conditions: 'ظروف الإضاءة',
    noise_level: 'مستوى الضوضاء',
    temperature: 'درجة الحرارة',
    
    weather_placeholder: 'مشمس، ممطر، عاصف، إلخ.',
    lighting_placeholder: 'جيد، سيء، كافٍ، إلخ.',
    noise_placeholder: 'عالي، عادي، منخفض',
    temperature_placeholder: 'درجة مئوية',
    
    work_type: 'نوع العمل',
    work_height: 'ارتفاع العمل',
    experience_level: 'مستوى الخبرة',
    shift_time: 'الوردية',
    work_duration: 'مدة العمل',
    
    work_type_placeholder: 'التجميع والصيانة والنقل وغيرها',
    work_height_placeholder: 'بالمتر',
    experience_placeholder: 'بالسنة',
    shift_placeholder: 'صباح، مساء، ليل',
    
    // Report Content Hint
    report_content_hint_title: 'يرجى توضيح ما يلي:',
    report_content_hint_body: 'ماذا حدث؟ أين حدث؟ متى حدث؟ من كان متورطًا؟ صف تسلسل الأحداث بوضوح.',
    
    // Weather Options
    weather_sunny: 'مشمس',
    weather_cloudy: 'غائم',
    weather_rainy: 'ممطر',
    weather_snowy: 'ثلجي',
    weather_windy: 'عاصف',
    weather_foggy: 'ضبابي',
    weather_stormy: 'عاصف جدًا',
    
    // Lighting Options
    lighting_excellent: 'ممتاز',
    lighting_good: 'جيد',
    lighting_adequate: 'كاف',
    lighting_poor: 'ضعيف',
    lighting_very_poor: 'ضعيف جدًا',
    
    // Noise Level Options
    noise_quiet: 'هادئ - أقل من 50 ديسيبل',
    noise_normal: 'عادي - 50-70 ديسيبل',
    noise_loud: 'عالي - 70-85 ديسيبل',
    noise_very_loud: 'عالي جدًا - أكثر من 85 ديسيبل',
    
    // Temperature Options
    temp_very_cold: 'بارد جدًا - أقل من 0°م',
    temp_cold: 'بارد - 0-10°م',
    temp_cool: 'معتدل البرودة - 10-15°م',
    temp_comfortable: 'مريح - 15-25°م',
    temp_warm: 'دافئ - 25-35°م',
    temp_hot: 'حار جدًا - أكثر من 35°م',
    
    // Work Type Options
    work_manual_labor: 'عمل يدوي',
    work_machine_operation: 'تشغيل الآلات',
    work_assembly: 'التجميع',
    work_construction: 'البناء',
    work_maintenance: 'الصيانة/الإصلاح',
    work_cleaning: 'التنظيف',
    work_driving: 'تشغيل المركبات',
    work_admin: 'عمل إداري',
    work_other: 'آخر',
    
    // Work Height Options
    height_ground_level: 'مستوى الأرض (0 م)',
    height_low: 'ارتفاع منخفض (1-2 م)',
    height_medium: 'ارتفاع متوسط (2-5 م)',
    height_high: 'مرتفع (5-10 م)',
    height_very_high: 'مرتفع جدًا (أكثر من 10 م)',
    height_confined_space: 'مساحة محصورة',
    
    // Experience Level Options
    exp_new_employee: 'موظف جديد (أقل من شهر)',
    exp_trainee: 'متدرب/قيد التدريب (1-3 أشهر)',
    exp_junior: 'مبتدئ (3-6 أشهر)',
    exp_experienced: 'ذو خبرة (6-12 شهر)',
    exp_senior: 'كبير الخبرة (1-5 سنوات)',
    exp_expert: 'خبير (أكثر من 5 سنوات)',
    
    // Shift Time Options
    shift_morning: 'الوردية الصباحية (06:00-14:00)',
    shift_afternoon: 'الوردية المسائية (14:00-22:00)',
    shift_night: 'الوردية الليلية (22:00-06:00)',
    shift_early_morning: 'الصباح الباكر (04:00-12:00)',
    shift_late_evening: 'المساء المتأخر (20:00-04:00)',
    shift_overtime: 'ساعات إضافية',
    shift_not_applicable: 'غير قابل للتطبيق',
    
    // Injury/Damages Section
    injury_type: 'نوع الإصابة',
    injury_severity: 'شدة الإصابة',
    body_part: 'الجزء المصاب من الجسم',
    medical_treatment: 'العلاج الطبي',
    property_damage: 'الأضرار المادية',
    
    injury_type_placeholder: 'جرح، كسر، كدمة، إلخ.',
    body_part_placeholder: 'الرأس، الذراع، الساق، إلخ.',
    medical_placeholder: 'الإسعافات الأولية، المستشفى، إلخ.',
    
    root_cause_initial: 'السبب الجذري (التقييم الأولي)',
    corrective_actions: 'الإجراءات التصحيحية',
    additional_notes: 'ملاحظات إضافية',
    
    root_cause_placeholder: 'ما هي الأسباب الجذرية؟',
    corrective_placeholder: 'التدابير الوقائية الموصى بها',
    notes_placeholder: 'معلومات مهمة أخرى',
    
    // Emergency & Buttons
    emergency_measures: 'إجراءات الطوارئ',
    save_draft: 'حفظ المسودة',
    submit_for_analysis: 'إرسال للتحليل',
    
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

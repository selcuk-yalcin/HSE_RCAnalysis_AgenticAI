# HITL Test Ortamı

Bu klasör, **Human-in-the-Loop (HITL)** sisteminin **test versiyonunu** içerir.
1. KULLANICI OLAY AÇIKLAMASI GİRER
   └─ (İlk başta kısıtlı bilgi: "Elektrik çarpması oldu")
   
2. SISTEM ANALIZ EDER (Overview + Assessment)
   ├─ Olay tipini tanımla
   ├─ Şiddeti belirle
   └─ Investigation level set et
   
3. SORU SORMA YAPISI DEVREYE GİRER (Knowledge Base'le entegre)
   ├─ Eksik kategorileri tespit et
   ├─ HSG245 kodlarına bağlı sorular üret
   └─ GRADIO arayüzü ile kullanıcıya sor
   
4. KULLANICI CEVAPLAR
   └─ Her cevap ile daha detaylı bilgi
   
5. ROOT CAUSE ANALYSIS (RootCauseAgentV2)
   ├─ Immediate Cause'tan başla
   ├─ 5-Why zinciri ile inerken sorular sor
   └─ Dallar halinde root causes belirle
   
6. RAPOR ÜRETİMİ (SkillBasedDocxAgent)
   └─ Toplanan tüm bilgilerle DOCX + HTML rapor

## ⚠️ ÖNEMLİ
Bu test ortamı, **ana sistem dosyalarını DEĞİŞTİRMEZ**. Sadece test amaçlıdır.

## 📁 Dosya Yapısı

```
hitl_test/
├── README.md                          # Bu dosya
├── hybrid_input_processor.py          # Girdi seviyesi tespit modülü
├── question_engine.py                 # Soru üretim motoru
├── gradio_app_test.py                 # Gradio test arayüzü
├── test_minimal_input.py              # Minimal giriş testi
├── test_detailed_input.py             # Detaylı giriş testi
└── templates/
    ├── incident_form_template.txt     # Form şablonu
    └── test_data_examples.txt         # Örnek test verileri
```

## 🚀 Çalıştırma

### Gradio Test Arayüzü
```bash
cd hitl_test
python gradio_app_test.py
```

Tarayıcıda: http://localhost:7860

### Testleri Çalıştır
```bash
# Minimal giriş testi
python test_minimal_input.py

# Detaylı giriş testi
python test_detailed_input.py
```

## 🔗 Ana Sistem ile Entegrasyon

Test başarılı olduğunda, ana sisteme entegre etmek için:

1. `hitl/` klasörünü ana dizine taşı
2. `api/main.py` içine HITL endpoint'leri ekle
3. Frontend (Infera) ile API bağlantısı kur

## 📌 Ana Sistemde DEĞİŞMEYEN Dosyalar

✅ Aşağıdaki dosyalar **HİÇ DEĞİŞTİRİLMEZ**:
- `agents/overview_agent.py`
- `agents/assessment_agent.py`
- `agents/rootcause_agent_v2.py`
- `agents/skillbased_docx_agent.py`
- `tests/test_*.py`

❌ Bu dosyalara **DOKUNMAYIN**!

## 🎯 Test Hedefleri

1. ✅ Girdi seviyesi tespiti doğru çalışıyor mu?
2. ✅ Soru üretimi mantıklı mı?
3. ✅ Kullanıcı cevapları doğru işleniyor mu?
4. ✅ Kod önerileri tutarlı mı?
5. ✅ Ana sistem agent'ları ile uyumlu mu?

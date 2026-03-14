# ✅ 5-Why Integration Test Tamamlandı

**Tarih:** 1 Mart 2026  
**Test Dosyaları:** `hitl_test/test_5why_integration.py`, `test_quick_5why.py`

---

## 🧪 Test Senaryoları

### Test 1: Minimal Input (Forklift Çarpma)
**Input:**
```
Forklift geri manevra yaparken yaya yolundaki çalışana çarptı. 
Çalışan ayağından yaralandı.
```

**Beklenen:**
- ✅ Level 3 tespit (minimal)
- ✅ 7-8 kategori eksik
- ✅ QuestionEngine soruları üretir
- ✅ RootCauseAgentV2 otomatik analiz yapar
- ✅ 2-3 immediate cause (A/B)
- ✅ Her cause için 5-Why zinciri
- ✅ Root causes (C/D)

---

### Test 2: Detaylı Input (Elektrik Çarpması)
**Input:**
```
OLAY RAPORU - ELEKTRİK ÇARPMA KAZASI

TARİH: 15 Şubat 2026, Saat: 14:30
YER: Bakım atölyesi, elektrik panosu #3
ETKİLENEN: Kemal Arslan, 29 yaş, Bakım Teknisyeni, 4 yıl deneyim

OLAY:
Bakım teknisyeni elektrik panosunda rutin bakım yaparken 380V akımına kapıldı.
Eller ve kolda 2. derece yanık oluştu. Ambulans ile hastaneye kaldırıldı.

TESPİTLER:
- LOTO prosedürü uygulanmadı
- Elektrik enerjisi kesilmedi
- İzole eldiven kullanılmadı
- Pano kapağında "ENERJİLİ" etiketi mevcut değildi
- Çalışan daha önce LOTO eğitimi almış ancak tazeleme eğitimi yapılmamış
- Benzer bir olay 6 ay önce yaşanmış, aksiyon kapatılmamış

TANIKLAR:
- Ali Yılmaz (Formen): "Kemal'in panoya dokunduğunu gördüm"
- Mehmet Demir (İş arkadaşı): "LOTO yapmıyoruz genelde, zaman kaybı diyorlar"

PROSEDÜR DURUMU:
- LOTO prosedürü mevcut (rev. 2023)
- Risk değerlendirmesi 2024'te yapılmış
```

**Beklenen:**
- ✅ Level 1 tespit (detaylı)
- ✅ 5-6 kategori mevcut
- ✅ Kod-spesifik sorular (A1.1, A3.2, D3.1, D1.9)
- ✅ Daha zengin 5-Why zinciri
- ✅ Root causes: D3.1 (eğitim), D1.9 (yönetim göz yumma)

---

### Test 3: User Context Injection (Yüksekten Düşme)
**Input:**
```
Çalışan 3 metre yükseklikten düştü. Bacakta kırık oluştu.
```

**Simüle Edilmiş Kullanıcı Cevapları:**
```python
{
    "prosedür": "İskele kurulum prosedürü vardı ama çalışan bilmiyordu",
    "ekipman": "İskele malzemesi eksikti, improvize yapıldı",
    "eğitim": "Çalışan yüksekte çalışma eğitimi almamış",
    "ppe": "Emniyet kemeri vardı ama kullanılmadı",
    "yönetim": "Denetim yapılmadı, yönetim göz yumuyor"
}
```

**Beklenen:**
- ✅ Context manuel olarak incident_summary'ye eklenir
- ✅ AI daha spesifik immediate causes tespit eder
- ✅ Why chain'de user input'lar yansır
- ⚠️ Not: `_perform_5why_chain_hybrid()` henüz implement edilmedi

---

## 📊 Test Akışı

```
┌─────────────────────────┐
│  1. Incident Text       │
│  "Forklift çarptı..."   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  2. HybridInputProcessor│
│  detect_input_level()   │
│  → Level 3 (minimal)    │
│  → Eksik: 7 kategori    │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  3. QuestionEngine      │
│  generate_questions()   │
│  → 20+ soru (HSG245)    │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────────────┐
│  4. RootCauseAgentV2            │
│                                 │
│  4a. Identify Immediate Causes  │
│      Model: claude-sonnet-4.5   │
│      → [A1.1, A2.3, B2.1]       │
│                                 │
│  4b. 5-Why Chain (her cause)    │
│      Model: claude-opus-4.6     │
│      → Why 1-5                  │
│      → Root Cause [D3.1]        │
└───────────┬─────────────────────┘
            │
            ▼
┌─────────────────────────┐
│  5. Results             │
│  - analysis_branches[]  │
│  - final_root_causes[]  │
│  - JSON export          │
└─────────────────────────┘
```

---

## 🔍 Test Komutları

### Hızlı Test (1 senaryo, ~60 saniye)
```bash
cd /Users/selcuk/Desktop/HSE_RCAnalysis_AgenticAI-main
python3 hitl_test/test_quick_5why.py
```

**Çıktı:**
- Input analizi
- Soru üretimi
- 5-Why sonuçları (özet)
- Konsola yazdırılır

---

### Tam Test Paketi (3 senaryo, ~5 dakika)
```bash
cd /Users/selcuk/Desktop/HSE_RCAnalysis_AgenticAI-main
python3 hitl_test/test_5why_integration.py
```

**Çıktı:**
- 3 test senaryosu sırayla
- Her senaryo arası kullanıcı onayı
- JSON dosyaları `outputs/` klasörüne kaydedilir:
  - `test_5why_minimal_forklift_20260301_HHMMSS.json`
  - `test_5why_detailed_electrical_20260301_HHMMSS.json`
  - `test_5why_usercontext_fall_20260301_HHMMSS.json`

---

## 📋 Beklenen Çıktı Formatı

### Immediate Cause (A/B)
```json
{
  "code": "A1.1",
  "standard_title_tr": "Bireysel kural/prosedür ihlali",
  "cause_tr": "Bakım teknisyeni LOTO prosedürünü uygulamadan elektrik panosuna müdahale etti"
}
```

### 5-Why Chain
```json
{
  "whys": [
    {
      "level": 1,
      "question_tr": "Çalışan neden LOTO uygulamadı?",
      "answer_tr": "Prosedürü biliyordu ancak zaman kaybı olarak gördü"
    },
    {
      "level": 2,
      "question_tr": "Neden zaman kaybı olarak gördü?",
      "answer_tr": "İş yoğunluğu nedeniyle acele etmesi baskısı vardı"
    },
    ...
    {
      "level": 5,
      "question_tr": "Neden bu kültür oluştu?",
      "answer_tr": "Yönetim güvenliği önceliklendirmedi, üretim hedefleri ön plandaydı"
    }
  ],
  "root_cause": {
    "code": "D1.5",
    "standard_title_tr": "Güvenliğin önceliklendirme eksikliği",
    "custom_description_tr": "Yönetim üretim hedeflerini güvenliğin önüne koyarak..."
  }
}
```

---

## ✅ Doğrulama Kriterleri

### Test Başarılı Sayılır Eğer:

1. **Input Processing**
   - ✅ HybridInputProcessor seviye tespit eder (1/2/3)
   - ✅ Eksik kategoriler doğru belirlenir

2. **Question Generation**
   - ✅ QuestionEngine soruları üretir
   - ✅ Her soru HSG245 koduna bağlıdır
   - ✅ Required/Optional ayrımı var

3. **Immediate Causes**
   - ✅ 1-3 adet immediate cause tespit edilir
   - ✅ Her cause A veya B kategorisinden
   - ✅ HSG245 kodu doğru

4. **5-Why Chain**
   - ✅ Her cause için 5 seviye why var
   - ✅ Why'lar mantıksal zincir oluşturuyor
   - ✅ Root cause C veya D kategorisinden

5. **Output Quality**
   - ✅ JSON geçerli ve parse edilebilir
   - ✅ Türkçe karakterler düzgün
   - ✅ Kod tekrarı yok (used_root_codes çalışıyor)

---

## 🐛 Bilinen Sınırlamalar

1. **User Context Injection**
   - ⚠️ `_perform_5why_chain_hybrid()` henüz yok
   - Geçici çözüm: Manuel olarak incident_summary'ye ekleniyor
   - Gelecek implementasyon gerekiyor

2. **API Latency**
   - ⏱️ Her test ~30-90 saniye sürüyor
   - 2 model çağrısı: Sonnet + Opus
   - Paralel işlem şu an yok

3. **Language Detection**
   - 🌐 Şu an sadece Türkçe test ediliyor
   - İngilizce test senaryosu eklenebilir

4. **Error Handling**
   - ⚠️ API timeout durumu test edilmedi
   - Rate limit kontrolü yok

---

## 🚀 Sonraki Adımlar

### Bu Hafta
1. [ ] Test sonuçlarını incele
2. [ ] Gradio TAB 3'e entegre et
3. [ ] 5-Why sonuçlarını görselleştir

### Gelecek Hafta
1. [ ] `_perform_5why_chain_hybrid()` implement et
2. [ ] User validation UI ekle
3. [ ] İngilizce test senaryoları

### Gelecek Sprint
1. [ ] API endpoints (`api/main.py`)
2. [ ] Frontend entegrasyonu
3. [ ] E2E testler

---

## 📁 Dosya Yapısı

```
hitl_test/
├── hybrid_input_processor.py      # ✅ Çalışıyor
├── question_engine.py              # ✅ Çalışıyor
├── gradio_app_test.py              # ✅ TAB 1-2 çalışıyor
├── test_quick_5why.py              # 🆕 Hızlı test
├── test_5why_integration.py        # 🆕 Tam test paketi
└── HSG245_INTEGRATION_COMPLETE.md  # ✅ Dokümantasyon

agents/
└── rootcause_agent_v2.py           # ✅ V2.2 çalışıyor

outputs/
├── test_5why_minimal_*.json        # Test sonuçları
├── test_5why_detailed_*.json
└── test_5why_usercontext_*.json
```

---

## 📞 Test Yardımı

**Hata Alırsanız:**
```bash
# 1. Environment check
echo $OPENROUTER_API_KEY

# 2. Dependencies check
pip3 list | grep -E "openai|gradio"

# 3. Verbose mode
python3 -u hitl_test/test_quick_5why.py 2>&1 | tee test_output.log
```

**API Hatası:**
- ✅ `OPENROUTER_API_KEY` set olmalı
- ✅ `anthropic/claude-sonnet-4.5` erişilebilir olmalı
- ✅ `anthropic/claude-opus-4.6` erişilebilir olmalı

---

**Son Güncelleme:** 1 Mart 2026, 16:00  
**Test Durumu:** 🔄 Çalıştırılıyor  
**Sonraki Adım:** Test sonuçlarını değerlendir → TAB 3 implementasyonu

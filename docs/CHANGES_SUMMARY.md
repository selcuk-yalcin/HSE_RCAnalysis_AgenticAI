# HITL Sistemi - Değişiklik Özeti

## 📋 Genel Bakış

Bu belge, **Human-in-the-Loop (HITL)** sistemi için yapılan tüm değişiklikleri ve **test ortamının** kurulumunu özetler.

---

## ✅ Oluşturulan Dosyalar (Test Ortamı)

### **Yeni Klasör: `hitl_test/`**

```
hitl_test/
├── README.md                          ✅ OLUŞTURULDU
│   └─ Test ortamı rehberi
│
├── hybrid_input_processor.py          ✅ OLUŞTURULDU
│   └─ Girdi seviyesi tespit modülü (Level 1/2/3)
│
├── gradio_app_test.py                 ✅ OLUŞTURULDU
│   └─ Gradio test arayüzü
│
└── (İleriki adımlar)
    ├── question_engine.py             ⏳ PLANLANDI
    ├── test_minimal_input.py          ⏳ PLANLANDI
    └── test_detailed_input.py         ⏳ PLANLANDI
```

---

## ✅ Oluşturulan Dokümantasyon

```
docs/
├── HITL_HYBRID_DESIGN.md              ✅ OLUŞTURULDU (Daha önce)
│   └─ Detaylı sistem tasarımı
│
└── FRONTEND_INTEGRATION_DESIGN.md     ✅ YENİ OLUŞTURULDU
    └─ Frontend (Infera) entegrasyon tasarımı
```

---

## ❌ DEĞİŞTİRİLMEYEN Ana Sistem Dosyaları

### **Agents (Hiç Dokunulmadı)**
```
agents/
├── overview_agent.py              ❌ DEĞİŞMEDİ
├── assessment_agent.py            ❌ DEĞİŞMEDİ
├── rootcause_agent_v2.py          ❌ DEĞİŞMEDİ
├── skillbased_docx_agent.py       ❌ DEĞİŞMEDİ (Sadece dil kuralı değişmişti - daha önce)
└── knowledge_base.py              ❌ DEĞİŞMEDİ
```

### **Tests (Hiç Dokunulmadı)**
```
tests/
├── test_electrical_shock 2.py     ❌ DEĞİŞMEDİ
├── test_fall_from_height 2.py     ❌ DEĞİŞMEDİ
├── test_fall_from_height_english.py  ❌ DEĞİŞMEDİ
└── (diğer test dosyaları)         ❌ DEĞİŞMEDİ
```

### **API (Henüz Dokunulmadı)**
```
api/
└── main.py                        ⏳ PLANLANDI (HITL endpoint'leri eklenecek)
```

---

## 🔍 Detaylı Değişiklik Listesi

### **1. `hitl_test/hybrid_input_processor.py`**

**Amaç:** Kullanıcı girdisini analiz eder ve seviye tespit eder.

**Fonksiyonlar:**
- `detect_input_level(incident_text)` → (level, details)
  - Level 1: Detaylı (8+ puan)
  - Level 2: Orta (4-7 puan)
  - Level 3: Minimal (0-3 puan)

- `generate_missing_questions(missing_categories, incident_type)` → List[Dict]
  - Eksik bilgiler için sorular üretir

**Test Kodu İçerir:**
```python
if __name__ == "__main__":
    # Test 1: Minimal
    # Test 2: Detaylı
```

**Ana sistemle bağlantı:** YOK (Bağımsız test modülü)

---

### **2. `hitl_test/gradio_app_test.py`**

**Amaç:** Gradio ile test arayüzü sağlar.

**Özellikler:**
- 4 Tab:
  1. Olay Girişi (3 örnek veri)
  2. Sorgulama (WIP)
  3. Kök Neden Analizi (WIP)
  4. Rapor (WIP)

**Port:** 7860 (localhost)

**Ana sistemle bağlantı:**
```python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
```
Sadece `hybrid_input_processor.py`'yi import eder.

---

### **3. `docs/FRONTEND_INTEGRATION_DESIGN.md`**

**Amaç:** Infera frontend platformuna nasıl entegre edileceğini gösterir.

**İçerik:**
- Mevcut Infera yapısı analizi
- 2 entegrasyon seçeneği:
  - **Option A:** Modal (Önerilen)
  - **Option B:** Yeni Tab (Part 2.5)
- Backend API tasarımı
- Frontend kod örnekleri (HTML/CSS/JS)
- Veri akışı şeması

**Önerilen API Endpoint'leri:**
```
POST /api/hitl/analyze-input
POST /api/hitl/get-next-question
POST /api/hitl/submit-answer
POST /api/hitl/generate-report
```

---

## 🚀 Çalıştırma Talimatları

### **Test Ortamını Çalıştırma**

#### 1. Gradio Arayüzü
```bash
cd /Users/selcuk/Desktop/HSE_RCAnalysis_AgenticAI-main/hitl_test
python gradio_app_test.py
```

Tarayıcıda: http://localhost:7860

#### 2. Girdi Analiz Testi
```bash
cd hitl_test
python hybrid_input_processor.py
```

Çıktı:
```
Test 1 - Minimal: Level 3, Eksik: ['kronoloji', 'prosedür', 'tanık', 'yönetim', ...]
Test 2 - Detaylı: Level 1, Mevcut: ['kronoloji', 'prosedür', 'tanık', 'yönetim']
```

---

## 📊 Sistem Karşılaştırması

### **ÖNCEKİ SİSTEM**
```
Kullanıcı → Part 1 → Part 2 → [AI Butonu] → Part 3 (Otomatik doldurulur)
```

**Sorun:**
- Kullanıcı müdahalesi yok
- AI hatalarını düzeltemez
- Eksik bilgi varsa sonuç kötü

### **YENİ SİSTEM (HITL)**
```
Kullanıcı → Part 1 → Part 2 → [AI + HITL Butonu] → Modal açılır
                                                      ↓
                                             Girdi analizi
                                                      ↓
                              Level 1?        Level 2/3?
                                 ↓               ↓
                            Direkt analiz    Sorular sor
                                 ↓               ↓
                           Part 3'e doldur  ← Yanıtları topla
```

**Avantaj:**
- ✅ Kullanıcı her aşamayı kontrol eder
- ✅ Eksik bilgileri AI sorar
- ✅ Kod önerilerini onayla/düzelt
- ✅ Daha kaliteli sonuç

---

## 🔄 Sonraki Adımlar

### **Faz 1: Test Ortamını Tamamlama** (1 hafta)
- [ ] `question_engine.py` kodunu yaz
- [ ] `test_minimal_input.py` oluştur
- [ ] `test_detailed_input.py` oluştur
- [ ] Gradio arayüzüne Tab 2 (Sorgulama) ekle

### **Faz 2: Backend API** (1 hafta)
- [ ] `api/main.py` içine HITL endpoint'leri ekle
- [ ] API testleri yaz
- [ ] Swagger dokümantasyonu güncelle

### **Faz 3: Frontend Entegrasyonu** (1-2 hafta)
- [ ] Modal component tasarla
- [ ] API fetch/axios entegrasyonu
- [ ] Part 3 otomatik doldurma
- [ ] Kullanıcı testleri

---

## ⚠️ Dikkat Edilmesi Gerekenler

### **1. Ana Sistem Bozulmasın**
```python
# ✅ DOĞRU: Test ortamı import'u
from hitl_test.hybrid_input_processor import HybridInputProcessor

# ❌ YANLIŞ: Ana agent'ları değiştirmek
# agents/rootcause_agent_v2.py dosyasını düzenleme!
```

### **2. API Endpoint'leri**
Ana sisteme endpoint eklerken:
```python
# ✅ DOĞRU: Yeni endpoint grubu
@app.post("/api/hitl/analyze-input")

# ❌ YANLIŞ: Mevcut endpoint'leri değiştirmek
@app.post("/api/analyze")  # Bunu değiştirme!
```

### **3. Frontend Değişiklikleri**
```javascript
// ✅ DOĞRU: Yeni buton ekle
<button onclick="openHITLModal()">AI + HITL</button>

// ❌ YANLIŞ: Mevcut AI butonunu sil
// <button onclick="aiAnalyze()">AI Powered</button>  ← Bunu silme!
```

---

## 📈 Başarı Metrikleri

Test başarısı için hedefler:

1. ✅ **Girdi Seviyesi Tespiti**
   - Minimal, orta, detaylı doğru tespit edilmeli
   - Test accuracy: >90%

2. ✅ **Soru Üretimi**
   - Olay tipine göre uygun sorular
   - Dallanma mantığı çalışmalı

3. ✅ **Ana Sistem Uyumluluğu**
   - Mevcut agent'lar bozulmadan çalışmalı
   - API endpoint'leri backward compatible

4. ✅ **Performans**
   - Girdi analizi: <1 saniye
   - Soru üretimi: <2 saniye
   - Toplam akış: <30 saniye (10 soru için)

---

## 📞 Destek

Sorularınız için:
- **Tasarım:** `docs/HITL_HYBRID_DESIGN.md`
- **Frontend:** `docs/FRONTEND_INTEGRATION_DESIGN.md`
- **Test:** `hitl_test/README.md`

---

**SON GÜNCELLEME:** 1 Mart 2026  
**DURUM:** Test ortamı hazır, backend ve frontend entegrasyonu bekliyor ✅

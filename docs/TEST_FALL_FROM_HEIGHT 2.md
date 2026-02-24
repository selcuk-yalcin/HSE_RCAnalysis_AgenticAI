# Test Dokümantasyonu: Yüksekten Düşme Olayı

## 📋 Genel Bilgiler

**Test Dosyası:** `test_fall_from_height.py`  
**Olay Tipi:** İnşaat İşkolunda Yüksekten Düşme  
**Şiddet:** Fatal/Major Injury  
**RIDDOR Durumu:** Evet (>2m yükseklikten düşme)

---

## 🎯 Test Amacı

Bu test, inşaat şantiyesinde iskele montajı sırasında meydana gelen **yüksekten düşme olayının** tam sistemli kök neden analizini doğrulamak içindir.

### Test Kapsamı:
1. **Ortam Kontrolü** - API anahtarları ve bağımlılıkların doğrulanması
2. **OverviewAgent** - Olayın ilk değerlendirmesi ve sınıflandırılması
3. **AssessmentAgent** - RIDDOR uygunluğu ve soruşturma seviyesi belirlenmesi
4. **RootCauseAgentV2** - HSG245 metodolojisi ile hiyerarşik 5-Why analizi
5. **SkillBasedDocxAgent** - Profesyonel rapor üretimi (DOCX + HTML)
6. **Kalite Kontrolü** - Çıktıların doğrulanması

---

## 📖 Olay Senaryosu

### Olay Özeti:
**Tarih:** 18 Şubat 2026, 10:35  
**Lokasyon:** Yapı İnşaat Şantiyesi - 4. Kat İskele Alanı  
**Etkilenen:** Hasan Yıldız (32), İskele Montaj İşçisi  

### Ne Oldu:
İşçi **6 metre yükseklikteki iskeleden** düşerek zemine çakıldı. L2 omurga kırığı, pelvis çatlağı ve iç kanama meydana geldi. İşçi yoğun bakıma alındı.

### Kritik Faktörler:
- ✗ **Emniyet kemeri takılmamış** (prosedür ihlali)
- ✗ **İskele korkuluğu eksik** (montaj tamamlanmamış)
- ✗ **Güvenlik ağı yok**
- ✓ Baret takılı
- ✓ İş ayakkabısı giyili

---

## 🔍 Beklenen Kök Nedenler

Test sonucunda **3-4 organizasyonel kök neden** beklenmektedir:

### 1. **Prosedür İhlali (A Kategorisi - İnsan)**
- Emniyet kemeri takma prosedürüne uyulmamış
- "Herkes öyle yapıyor" normalleşmesi

### 2. **Risk Değerlendirmesi Yetersizliği (D Kategorisi - Organizasyonel)**
- İskele iş izin sistemi eksik çalışıyor
- Yüksekte çalışma risk değerlendirmesi güncel değil

### 3. **Eğitim Eksikliği (D Kategorisi - Organizasyonel)**
- İşbaşı eğitimi kayıtları eksik
- Yüksekte çalışma eğitimi verilmemiş

### 4. **Üretim Baskısı (D Kategorisi - Organizasyonel)**
- Proje 3 hafta gecikmeli
- "Hızlı bitir" talimatı - güvenliğin önceliksizleşmesi
- Korkuluk montajı tamamlanmadan çalışma

---

## 🔄 Test Akışı

```
┌─────────────────────────────────────────────────────────────┐
│ ADIM 1: Ortam Kontrolü                                      │
│  • API Key doğrulama (OPENROUTER_API_KEY)                   │
│  • Python paketleri kontrolü (openai, docx, requests)       │
│  • outputs/ dizini hazırlığı                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ADIM 2: OverviewAgent                                       │
│  Input:  INCIDENT_DATA (olay raporu metni)                  │
│  Process: AI ile brief details extraction                   │
│  Output:  part1 = {ref_no, incident_type, brief_details}    │
│           • ref_no: INC-20260218-XXXXXX                      │
│           • incident_type: "Major injury" veya "Serious"     │
│           • what/where/when/who/emergency                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ADIM 3: AssessmentAgent                                     │
│  Input:  part1 + INCIDENT_DATA                              │
│  Process: Şiddet, RIDDOR, investigation level analizi       │
│  Output:  part2 = {                                          │
│             actual_potential_harm: "1. Fatal or major"       │
│             riddor.reportable: "Y"                           │
│             investigation.level: "High level"                │
│             investigation.priority: "High"                   │
│             investigation.team: [...]                        │
│           }                                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ADIM 4: RootCauseAgentV2                                    │
│  Input:  part1 + part2 + INCIDENT_DATA                      │
│  Process: HSG245 Hierarchical 5-Why Analysis                │
│           1. Doğrudan nedenleri belirle (A/B kategori)       │
│           2. Her dal için 5-Why zinciri oluştur             │
│           3. Kök nedenleri tespit et (C/D kategori)          │
│  Output:  part3 = {                                          │
│             analysis_branches: [                             │
│               {branch_number, why_chain[], root_cause}       │
│             ],                                               │
│             final_root_causes: [                             │
│               {code, title, category, description}           │
│             ],                                               │
│             analysis_method: {...}                           │
│           }                                                  │
│  Save:   outputs/fall_from_height_TIMESTAMP.json            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ADIM 5: SkillBasedDocxAgent                                 │
│  Input:  {part1, part2, part3_rca}                          │
│  Process: OpenRouter Claude API ile içerik üretimi          │
│           • CONTENT_SYSTEM_PROMPT + ham veri                │
│           • max_tokens: 32000, temperature: 0.3             │
│           • Non-streaming mode (hızlı ve güvenilir)         │
│  Output:  1. DOCX Rapor (18-20 sayfa):                      │
│              • Kapak sayfası                                 │
│              • Yönetici özeti                                │
│              • Olay detayları                                │
│              • Analiz metodu (HSG245)                        │
│              • Analiz dalları (5-Why zincirleri)             │
│              • Nihai kök nedenler                            │
│              • Düzeltici faaliyetler                         │
│              • Çıkarılan dersler                             │
│              • Sonuç ve öneriler                             │
│              • İmza sayfası                                  │
│           2. HTML Rapor (düzenlenebilir):                    │
│              • Modern, responsive tasarım                    │
│              • contenteditable=true (tüm alanlar)            │
│              • Renk kodlu bölümler                           │
│              • Print-friendly CSS                            │
│  Save:   outputs/INC-XXXXXXXX_fall_from_height.docx         │
│          outputs/INC-XXXXXXXX_fall_from_height.html         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ SONUÇ: Başarı Kontrolü                                      │
│  • Tüm adımlar PASSED mi?                                   │
│  • DOCX boyutu 50+ KB mı? (tam içerik)                      │
│  • HTML boyutu 15+ KB mı?                                   │
│  • JSON kök neden sayısı 3-4 mü?                            │
│  ✅ PASSED → sys.exit(0)                                    │
│  ❌ FAILED → sys.exit(1)                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Beklenen Çıktılar

### 1. JSON Dosyası
**Dosya:** `outputs/fall_from_height_YYYYMMDD_HHMMSS.json`  
**Boyut:** ~16-20 KB  
**İçerik:**
```json
{
  "analysis_branches": [
    {
      "branch_number": 1,
      "branch_title": "DAL 1 - KOŞULSAL",
      "direct_cause_code": "B1.3",
      "why_chain": [
        {"number": 1, "question": "...", "answer": "...", "code": "C"},
        ...
        {"number": 5, "question": "...", "answer": "...", "code": "D"}
      ],
      "root_cause_code": "D3.2",
      "root_cause_title": "Eğitim ihtiyaçlarının belirlenmemesi"
    }
  ],
  "final_root_causes": [
    {
      "root_cause_code": "D3.2",
      "root_cause_title": "...",
      "root_cause_category": "ORGANİZASYONEL",
      "detailed_description": "..."
    }
  ]
}
```

### 2. DOCX Raporu
**Dosya:** `outputs/INC-XXXXXXXX_fall_from_height.docx`  
**Boyut:** 50-60 KB  
**Sayfa:** 18-20  
**Format:** Profesyonel HSE raporu, renkli tablolar, grafik öğeler

### 3. HTML Raporu
**Dosya:** `outputs/INC-XXXXXXXX_fall_from_height.html`  
**Boyut:** 15-20 KB  
**Özellikler:**
- Düzenlenebilir tüm alanlar (`contenteditable="true"`)
- Responsive tasarım
- HSE renk paleti (koyu mavi, kırmızı, turuncu, yeşil)
- LocalStorage otomatik kayıt
- Print-to-PDF desteği

---

## ✅ Başarı Kriterleri

Test başarılı sayılır eğer:

1. ✅ **Tüm 5 adım PASSED** durumunda
2. ✅ **RIDDOR: Y** olarak tespit edildi
3. ✅ **Investigation Level: High level**
4. ✅ **Kök neden sayısı: 3-4**
5. ✅ **DOCX boyutu: >50 KB** (tam içerik)
6. ✅ **HTML boyutu: >15 KB**
7. ✅ **JSON geçerli ve ayrıştırılabilir**

---

## 🚀 Çalıştırma

```bash
# Virtual environment aktif et
source .venv/bin/activate

# Testi çalıştır
python test_fall_from_height.py

# Çıktıları kontrol et
ls -lh outputs/INC-*fall_from_height.*
```

---

## 🐛 Sorun Giderme

### Sorun: API kredi yetersiz
**Hata:** `Error code: 402 - requires more credits`  
**Çözüm:** OpenRouter hesabına kredi ekleyin

### Sorun: DOCX sadece kapak sayfası
**Hata:** Boyut 37 KB, içerik eksik  
**Çözüm:** `stream: False` olduğundan emin olun, `max_tokens=32000`

### Sorun: Import hatası
**Hata:** `ModuleNotFoundError: No module named 'agents'`  
**Çözüm:** Ana dizinden çalıştırdığınızdan emin olun

---

## 📚 İlgili Dokümanlar

- [HSG245 Metodolojisi](../docs/HSG245_methodology.md)
- [RIDDOR Raporlama Rehberi](../docs/RIDDOR_guide.md)
- [5-Why Tekniği](../docs/5why_technique.md)
- [Test Sistemi Genel Bakış](./README.md)

---

**Son Güncelleme:** 23 Şubat 2026  
**Versiyon:** 1.0  
**Yazar:** HSE RCA Test Sistemi

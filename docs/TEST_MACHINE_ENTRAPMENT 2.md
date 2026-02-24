# Test Dokümantasyonu: Makine Sıkışması Olayı

## 📋 Genel Bilgiler

**Test Dosyası:** `test_machine_entrapment.py`  
**Olay Tipi:** Makine Sıkışması / Ezilme Yaralanması  
**Şiddet:** Major Injury  
**RIDDOR Durumu:** Evet (7+ gün iş göremezlik, kırık)

---

## 🎯 Test Amacı

Bu test, konveyör bandı operatörlüğü sırasında **çalışan makineye müdahale** nedeniyle meydana gelen **parmak ezilmesi/kırığı olayının** kök neden analizini doğrulamak içindir.

### Test Kapsamı:
1. **Ortam Kontrolü** - API ve sistem hazırlığı
2. **OverviewAgent** - Makine kazası sınıflandırması
3. **AssessmentAgent** - Şiddet değerlendirmesi ve RIDDOR uygunluğu
4. **RootCauseAgentV2** - Makine güvenliği ihlallerinin kök neden analizi
5. **SkillBasedDocxAgent** - Makine güvenliği odaklı rapor (DOCX + HTML)
6. **Kalite Kontrolü** - Guard/barrier eksikliklerinin tespiti

---

## 📖 Olay Senaryosu

### Olay Özeti:
**Tarih:** 20 Şubat 2026, 08:45  
**Lokasyon:** Paketleme Hattı - Konveyör Band Sistemi (KB-05)  
**Etkilenen:** Fatma Yılmaz (27), Konveyör Band Operatörü  

### Ne Oldu:
Operatör, **çalışır durumdaki konveyör bandında** karton kutu sıkışması oluşunca **makineyi durdurmadan** müdahale etti. Sağ eli konveyör bantla tambur arasında sıkıştı. **3 parmağında ezilme ve açık kırık** meydana geldi.

### Kritik Faktörler:
- ✗ **Makine çalışırken müdahale** (MAJOR violation)
- ✗ **Koruyucu/guard çıkarılmış** (daha önce sökülmüş)
- ✗ **Işık perdesi/light curtain yok**
- ✗ **Acil stop düğmesi erişimsiz** (karton yığınının arkasında)
- ✗ **Kronik arıza sorunlu band** (haftada 3-4 kez sıkışma)
- ✗ **İş talimatı: "Makineyi durdur" adımı yok**
- ✓ Eldiven takılıydı (ancak yardımcı olmadı)

---

## 🔍 Beklenen Kök Nedenler

Test sonucunda **3-4 organizasyonel kök neden** beklenmektedir, özellikle **makine güvenliği eksiklikleri**:

### 1. **Koruyucu (Guard) Çıkarılması Normalleşmesi (D4.1 - Organizasyonel)**
- Guard sökme yaygınlaşmış ("daha kolay erişim")
- Yönetim farkında ama önlem almıyor
- "Üretimi aksatmayalım" kültürü

### 2. **Risk Değerlendirmesi Eksik/Güncel Değil (D1.5 - Organizasyonel)**
- Konveyör riski RA yapılmamış
- Guard çıkarma riski değerlendirilmemiş
- Makine tehlike analizi (MHA) yok

### 3. **Makine Bakımı Yetersiz (D2.2 - Organizasyonel)**
- Kronik sıkışma sorunu 6 aydır devam ediyor
- Önleyici bakım planı işlemiyor
- Yedek parça tedarik süresi uzun

### 4. **İş Talimatı Yetersiz (D3.1 - Organizasyonel)**
- "Makineyi durdur" adımı eksik
- Safe work procedure (SWP) güncellenmemiş
- LOTO talimatı yok

---

## 🔄 Test Akışı

```
┌─────────────────────────────────────────────────────────────┐
│ ADIM 1: Ortam Kontrolü                                      │
│  • OPENROUTER_API_KEY doğrulama                             │
│  • agents modülü import kontrolü                            │
│  • outputs/ dizini hazırlık                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ADIM 2: OverviewAgent                                       │
│  Input:  INCIDENT_DATA (konveyör sıkışması raporu)          │
│  Process: Olay tipi "Machinery entrapment" tespit           │
│  Output:  part1 = {                                          │
│             ref_no: "INC-20260220-XXXXXX"                    │
│             incident_type: "Major injury - Machinery"        │
│             brief_details: {                                 │
│               what: "Konveyör sıkışması, 3 parmak kırığı"    │
│               who: "Fatma Yılmaz, Operatör"                  │
│               when: "20.02.2026, 08:45"                      │
│               where: "Paketleme Hattı, Konveyör KB-05"       │
│               how: "Çalışan makineye müdahale"               │
│             }                                                │
│           }                                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ADIM 3: AssessmentAgent                                     │
│  Input:  part1 + INCIDENT_DATA                              │
│  Process: Kırık + 4 ay iş göremezlik → Major şiddet         │
│           RIDDOR reportable (7+ gün)                        │
│  Output:  part2 = {                                          │
│             actual_potential_harm: "2. Major injury"         │
│             riddor.reportable: "Y"                           │
│             riddor.reason: "Over-7-day injury, fracture"     │
│             investigation.level: "Medium-High level"         │
│             investigation.priority: "High"                   │
│             investigation.team: [                            │
│               "HSE Manager", "Mechanical Engineer",          │
│               "Production Manager", "Maintenance Lead"       │
│             ],                                               │
│             investigation.specialist: [                      │
│               "Machine safety expert",                       │
│               "Ergonomics specialist"                        │
│             ]                                                │
│           }                                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ADIM 4: RootCauseAgentV2 - Machine Safety Focus            │
│  Input:  part1 + part2 + INCIDENT_DATA                      │
│  Process: HSG245 Hierarchical 5-Why                         │
│           Özel Odak: Guard eksiklikleri, bakım, kültür      │
│                                                              │
│  Analiz Dalları:                                             │
│  • DAL 1: Guard neden çıkarılmış?                           │
│    → Why 1: Erişim zordu, "kolaylık" için sökülmüş         │
│    → Why 2: Süpervizör uyarı vermemiş                       │
│    → Why 3: Guard olmadan çalışma normalize olmuş          │
│    → Why 4: Yönetim uygunsuzluğu görmüş ama onaylamış      │
│    → Why 5: Kök neden D4.1 (Güvenlik kültürü zayıf)        │
│                                                              │
│  • DAL 2: Kronik sıkışma neden çözülmedi?                  │
│    → Why 1: Bakım öncelik vermedi                           │
│    → Why 2: Önleyici bakım planı yok                        │
│    → Why 3: Bakım kaynaklarını yetersiz                     │
│    → Why 4: Yönetim bakım bütçesini kısıtladı              │
│    → Why 5: Kök neden D2.2 (Bakım yönetimi eksik)          │
│                                                              │
│  • DAL 3: Risk değerlendirmesi neden güncel değil?         │
│    → Why 1: RA 3 yıl önce yapılmış, güncellenmemiş         │
│    → Why 2: RA gözden geçirme prosedürü yok                │
│    → Why 3: Değişiklik yönetimi işlemiyor                  │
│    → Why 4: HSE-operasyon koordinasyonu zayıf              │
│    → Why 5: Kök neden D1.5 (RA sistemi eksik)              │
│                                                              │
│  • DAL 4 (opsiyonel): İş talimatı neden yetersiz?          │
│    → Why 5: Kök neden D3.1 (SWP güncelleme eksik)          │
│                                                              │
│  Output:  part3 = {                                          │
│             analysis_branches: [3-4 dal],                    │
│             final_root_causes: [                             │
│               D4.1, D2.2, D1.5, (D3.1 opsiyonel)            │
│             ],                                               │
│             contributing_factors: [                          │
│               "Chronic jamming issue",                       │
│               "Guard removed",                               │
│               "No light curtain",                            │
│               "Emergency stop inaccessible"                  │
│             ]                                                │
│           }                                                  │
│  Save:   outputs/machine_entrapment_TIMESTAMP.json          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ADIM 5: SkillBasedDocxAgent - Machine Safety Report        │
│  Input:  {part1, part2, part3_rca}                          │
│  Process: OpenRouter Claude Sonnet 4.5                      │
│           • Özel vurgu: Makine güvenliği standartları       │
│           • BS EN ISO 12100:2010 referansı                  │
│           • Risk azaltma hiyerarşisi                        │
│           • max_tokens: 32000                               │
│           • stream: False                                   │
│                                                              │
│  Output:  1. DOCX (18-22 sayfa):                            │
│              Bölüm 3: "Makine Güvenliği ve Koruyucular"     │
│              Bölüm 5: "Guard Eksikliği Analizi"             │
│              Bölüm 7: "Önleyici Bakım Sistemi Önerileri"    │
│              Bölüm 8: "Risk Azaltma Hiyerarşisi"            │
│              Ek: "BS EN ISO 12100 Uyumluluk Checklist"      │
│                                                              │
│           2. HTML (düzenlenebilir):                          │
│              Kırmızı: Guard eksikliği vurguları             │
│              Turuncu: Bakım sorunları                        │
│              Yeşil: Düzeltici faaliyetler                   │
│              Mavi: Risk azaltma önerileri                   │
│              Tablo: Light curtain maliyet-fayda             │
│                                                              │
│  Save:   outputs/INC-XXXXXXXX_machine_entrapment.docx       │
│          outputs/INC-XXXXXXXX_machine_entrapment.html       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ SONUÇ: Makine Güvenliği Analizi Doğrulama                  │
│  ✅ RIDDOR: Y (7+ gün)                                      │
│  ✅ Investigation Level: Medium-High                        │
│  ✅ Kök neden D4.1 (Kültür) tespit edildi mi?               │
│  ✅ Kök neden D2.2 (Bakım) tespit edildi mi?                │
│  ✅ Guard eksikliği contributing factor olarak listelendi?  │
│  ✅ DOCX >50 KB                                             │
│  ✅ HTML >15 KB                                             │
│  ✅ Risk azaltma hiyerarşisi raporda var mı?                │
│  → sys.exit(0) veya sys.exit(1)                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Beklenen Çıktılar

### 1. JSON Dosyası
**Dosya:** `outputs/machine_entrapment_YYYYMMDD_HHMMSS.json`  
**Boyut:** ~19-24 KB  
**Özel İçerik:**
```json
{
  "analysis_branches": [
    {
      "branch_number": 1,
      "branch_title": "DAL 1 - KORUYUCU (GUARD) EKSİKLİĞİ",
      "direct_cause_code": "B2.1",
      "direct_cause_title": "Koruyucu/barrier yetersiz",
      "why_chain": [
        {
          "number": 1,
          "question": "Koruyucu neden çıkarılmış?",
          "answer": "Erişim zordu, sökülmüş",
          "code": "C"
        },
        ...
        {
          "number": 5,
          "question": "Yönetim neden onayladı?",
          "answer": "Üretim önceliği kültürü, güvenlik 2. planda",
          "code": "D"
        }
      ],
      "root_cause_code": "D4.1",
      "root_cause_title": "Güvenlik kültürü eksikliği"
    },
    {
      "branch_number": 2,
      "branch_title": "DAL 2 - KRONİK BAKIMSIZLIK",
      "root_cause_code": "D2.2",
      "root_cause_title": "Önleyici bakım sistemi yetersiz"
    }
  ],
  "final_root_causes": [
    {
      "root_cause_code": "D4.1",
      "root_cause_category": "ORGANİZASYONEL",
      "root_cause_title": "Güvenlik kültürü eksikliği",
      "detailed_description": "Guard sökme normalize, üretim-güvenlik çatışması"
    },
    {
      "root_cause_code": "D2.2",
      "root_cause_category": "ORGANİZASYONEL",
      "root_cause_title": "Önleyici bakım yetersiz",
      "detailed_description": "Kronik sıkışma 6 aydır çözülmedi, bakım kaynakları yetersiz"
    },
    {
      "root_cause_code": "D1.5",
      "root_cause_category": "ORGANİZASYONEL",
      "root_cause_title": "Risk değerlendirmesi güncel değil",
      "detailed_description": "RA 3 yıl önce, guard eksikliği risk olarak görülmemiş"
    }
  ],
  "contributing_factors": [
    {
      "factor": "Kronik sıkışma sorunu",
      "impact": "Yüksek"
    },
    {
      "factor": "Guard çıkarılmış",
      "impact": "Kritik"
    },
    {
      "factor": "Işık perdesi (light curtain) yok",
      "impact": "Yüksek"
    }
  ]
}
```

### 2. DOCX Raporu - Machine Safety Focused
**Dosya:** `outputs/INC-XXXXXXXX_machine_entrapment.docx`  
**Boyut:** 54-64 KB  
**Özel Bölümler:**
- **Bölüm 3.3:** "Makine Koruyucuları ve BS EN ISO 12100"
- **Bölüm 5.2:** "Guard Eksikliği Kök Neden Analizi"
- **Bölüm 6.1:** "Kronik Bakım Sorunları"
- **Bölüm 7.1:** "Risk Azaltma Hiyerarşisi (Elimination → Guard → PPE)"
- **Bölüm 8.2:** "Işık Perdesi (Light Curtain) Maliyet-Fayda Analizi"
- **Ek A:** "Konveyör Güvenlik Standartları Checklist"

### 3. HTML Raporu - Interactive & Editable
**Dosya:** `outputs/INC-XXXXXXXX_machine_entrapment.html`  
**Boyut:** 17-23 KB  
**Özel Özellikler:**
- Kırmızı badge: "GUARD EKSİK", "MAJOR VIOLATION"
- Turuncu: Bakım eksiklikleri
- Mavi: Risk azaltma önerileri
- Düzenlenebilir: Bakım planı tablosu
- Interaktif: Light curtain ROI hesaplayıcı

---

## ✅ Başarı Kriterleri

Makine güvenliği odaklı başarı kriterleri:

1. ✅ **RIDDOR: Y** (>7 gün, kırık)
2. ✅ **Investigation Level: Medium-High**
3. ✅ **Kök neden D4.1** (Güvenlik Kültürü) tespit edildi
4. ✅ **Kök neden D2.2** (Bakım Eksikliği) tespit edildi
5. ✅ **Contributing Factor:** "Guard çıkarılmış" tespit edildi
6. ✅ **Contributing Factor:** "Kronik sıkışma" tespit edildi
7. ✅ **Düzeltici faaliyet:** Light curtain önerisi var
8. ✅ **Risk azaltma hiyerarşisi** raporda açıklandı
9. ✅ **DOCX >50 KB** ve makine güvenliği bölümleri var
10. ✅ **HTML >15 KB** ve düzenlenebilir

---

## 🚀 Çalıştırma

```bash
# Virtual environment
source .venv/bin/activate

# Test çalıştır
python test_machine_entrapment.py

# Guard eksikliği analizi kontrol
grep -i "guard\|koruyucu\|barrier" outputs/machine_entrapment_*.json

# Bakım sorunları kontrol
grep -i "maintenance\|bakım" outputs/machine_entrapment_*.json

# Rapor boyutu kontrol
ls -lh outputs/INC-*machine_entrapment.*
```

---

## 🐛 Machine Safety Sorun Giderme

### Sorun: D4.1 (kültür) tespit edilmedi
**Olası Neden:** AI "guard çıkarma"yı tek seferlik olay gördü  
**Çözüm:** Prompt'a "normalize olmuş" ifadesini ekleyin, "yönetim farkında" vurgulayın

### Sorun: D2.2 (bakım) eksik
**Olası Neden:** "Kronik arıza" bilgisi gözden kaçtı  
**Çözüm:** INCIDENT_DATA'da "6 aydır devam eden" ifadesini netleştirin

### Sorun: Light curtain önerisi raporda yok
**Olası Neden:** AI sadece guard takma önerdi  
**Çözüm:** "Mühendislik kontrolleri (light curtain, iki el kumanda)" vurgusunu artırın

---

## 📚 Makine Güvenliği Referanslar

- [BS EN ISO 12100:2010 - Machinery Safety](https://www.iso.org/standard/51528.html)
- [BS EN ISO 13857:2019 - Safety Distances](https://www.iso.org/standard/69569.html)
- [HSE INDG229 - Safe Use of Work Equipment](https://www.hse.gov.uk/pubns/indg229.pdf)
- [PUWER 1998 - UK Machinery Regulations](https://www.hse.gov.uk/work-equipment-machinery/puwer.htm)
- [IEC 61508 - Functional Safety](https://www.iec.ch/functional-safety)

---

## 🔗 İlgili Testler

- [Test: Yüksekten Düşme](./TEST_FALL_FROM_HEIGHT.md) - Guard/barrier karşılaştırması
- [Test: Elektrik Çarpması](./TEST_ELECTRICAL_SHOCK.md) - Üretim baskısı kültürü benzerliği

---

## 📈 Risk Azaltma Hiyerarşisi

Test raporunda aşağıdaki hiyerarşi beklenmektedir:

```
1️⃣ ELIMINATION (En İyi)
   ↓ Konveyör sıkışmasını önle → Band kalitesi iyileştir

2️⃣ SUBSTITUTION
   ↓ Otomatik temizleme sistemi

3️⃣ ENGINEERING CONTROLS
   ↓ Light curtain + interlocked guard + two-hand control

4️⃣ ADMINISTRATIVE CONTROLS
   ↓ LOTO prosedürü + SWP güncelleme + eğitim

5️⃣ PPE (En Zayıf)
   ↓ Eldiven (yetersiz - asıl çözüm değil)
```

---

## 🎓 Ders Çıkarımları

Bu test senaryosundan beklenen öğrenimler:

1. **Normalized Deviance (Normalleşme):** Guard sökme yaygınlaşmış, tehlikeli durumlar "normal" olarak kabul edilmiş
2. **Production Pressure:** "Üretimi aksatma" kültürü, güvenlik tedbirlerinin atlanmasına yol açıyor
3. **Chronic Issues Ignored:** Kronik arızalar "kabul edilir" hale gelmiş, kök neden çözülmemiş
4. **Hierarchy of Controls:** PPE en zayıf kontrol, mühendislik kontrolleri öncelikli

---

**Son Güncelleme:** 23 Şubat 2026  
**Versiyon:** 1.0  
**Özel Odak:** Makine Güvenliği ve Koruyucular  
**Standartlar:** BS EN ISO 12100, PUWER 1998  
**Yazar:** HSE RCA Test Sistemi

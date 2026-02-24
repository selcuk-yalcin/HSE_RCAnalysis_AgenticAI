# Test Dokümantasyonu: Elektrik Çarpması Olayı

## 📋 Genel Bilgiler

**Test Dosyası:** `test_electrical_shock.py`  
**Olay Tipi:** Elektrikle Temas / Elektrik Çarpması  
**Şiddet:** Fatal/Major Injury  
**RIDDOR Durumu:** Evet (kardiyak arrest, hastane yatışı)

---

## 🎯 Test Amacı

Bu test, elektrik panosunda **LOTO (Lockout/Tagout) prosedürü uygulanmadan** yapılan bakım çalışması sırasında meydana gelen **elektrik çarpması olayının** kök neden analizini doğrulamak içindir.

### Test Kapsamı:
1. **Ortam Kontrolü** - API ve bağımlılık doğrulaması
2. **OverviewAgent** - Elektrik olayı sınıflandırması
3. **AssessmentAgent** - Şiddet, RIDDOR ve soruşturma seviyesi
4. **RootCauseAgentV2** - LOTO prosedürü ihlalinin kök neden analizi
5. **SkillBasedDocxAgent** - Profesyonel rapor (DOCX + HTML)
6. **Kalite Kontrolü** - LOTO odaklı kök nedenlerin doğrulanması

---

## 📖 Olay Senaryosu

### Olay Özeti:
**Tarih:** 22 Şubat 2026, 14:20  
**Lokasyon:** Üretim Tesisi - Ana Dağıtım Panosu (ADP-3)  
**Etkilenen:** Kemal Arslan (29), Elektrik Bakım Teknisyeni  

### Ne Oldu:
Teknisyen **380V elektrik panosunda** **enerji kesintisi yapmadan** (LOTO prosedürü uygulamadan) bakım çalışması yaparken elektrik akımına kapıldı. **30 saniye süren kardiyak arrest** meydana geldi. 2. derece yanıklar oluştu.

### Kritik Faktörler:
- ✗ **LOTO prosedürü uygulanmadı** (MAJOR violation)
- ✗ **Enerji kaynağı açık** (380V AC)
- ✗ **Test cihazı kullanılmadı** (voltaj testi yapılmadı)
- ✗ **Gözlemci yok** (tek başına çalışma)
- ✗ **İzolasyon kilidi yok**
- ✗ **Uyarı etiketi asılmadı**
- ✓ Elektrik eldiveni vardı (ancak kullanmadı)
- ✓ Yalıtımlı ayakkabı

---

## 🔍 Beklenen Kök Nedenler

Test sonucunda **3-4 organizasyonel kök neden** beklenmektedir, özellikle **LOTO prosedürü eksiklikleri**:

### 1. **LOTO Eğitimi Yetersizliği (D3.2 - Organizasyonel)**
- Teknisyen LOTO eğitimi almamış
- Yetkili çalışan (Authorized Person) sertifikası yok
- Yenileme eğitimleri yapılmamış

### 2. **LOTO Prosedür İhlali Kültürü (D4.1 - Organizasyonel)**
- "Üretimi durdurmayalım" baskısı
- LOTO atlamak normalize olmuş
- Yönetim sessiz onayı

### 3. **İzleme ve Denetim Eksikliği (D1.4 - Organizasyonel)**
- LOTO uygulaması denetlenmiyor
- Çalışma izni sistemi yetersiz
- Yetki matrisi belirsiz

### 4. **Risk Değerlendirmesi Güncel Değil (D1.5 - Organizasyonel)**
- Elektrik riski RA yok veya eski
- Tek başına çalışma riski değerlendirilmemiş
- Acil durum planı eksik

---

## 🔄 Test Akışı

```
┌─────────────────────────────────────────────────────────────┐
│ ADIM 1: Ortam Kontrolü                                      │
│  • OPENROUTER_API_KEY kontrolü                              │
│  • Python paketleri (agents modülü dahil)                   │
│  • outputs/ dizini hazırlığı                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ADIM 2: OverviewAgent                                       │
│  Input:  INCIDENT_DATA (elektrik çarpması raporu)           │
│  Process: Olay tipi "Electrical shock" olarak tespit        │
│  Output:  part1 = {                                          │
│             ref_no: "INC-20260222-XXXXXX"                    │
│             incident_type: "Major injury - Electrical"       │
│             brief_details: {                                 │
│               what: "380V elektrik çarpması, LOTO yok"       │
│               who: "Kemal Arslan, Elektrik Teknisyeni"       │
│               when: "22.02.2026, 14:20"                      │
│               where: "ADP-3 Ana Dağıtım Panosu"              │
│             }                                                │
│           }                                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ADIM 3: AssessmentAgent                                     │
│  Input:  part1 + INCIDENT_DATA                              │
│  Process: Kardiyak arrest → Major/Serious şiddet            │
│           RIDDOR reportable (hospitalization >24h)          │
│  Output:  part2 = {                                          │
│             actual_potential_harm: "1. Fatal or major"       │
│             riddor.reportable: "Y"                           │
│             riddor.reason: "Hospitalization >24 hours"       │
│             investigation.level: "High level"                │
│             investigation.priority: "High"                   │
│             investigation.team: [                            │
│               "HSE Manager", "Electrical Engineer",          │
│               "Maintenance Supervisor", "Safety Rep"         │
│             ]                                                │
│           }                                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ADIM 4: RootCauseAgentV2 - LOTO Focused                    │
│  Input:  part1 + part2 + INCIDENT_DATA                      │
│  Process: HSG245 Hierarchical 5-Why                         │
│           Özel Odak: LOTO prosedür ihlali zincirleri        │
│                                                              │
│  Analiz Dalları:                                             │
│  • DAL 1: LOTO prosedürü neden uygulanmadı?                 │
│    → Why 1: Eğitim verilmemiş                               │
│    → Why 2: Eğitim planı yok                                │
│    → Why 3: Yetkinlik matrisi belirsiz                      │
│    → Why 4: İK-HSE koordinasyonu zayıf                      │
│    → Why 5: Kök neden D3.2 (Eğitim ihtiyacı belirsiz)      │
│                                                              │
│  • DAL 2: Üretim baskısı neden LOTO atlamaya yol açtı?     │
│    → Why 1: Duruş maliyeti çok yüksek görüldü              │
│    → Why 2: Güvenlik-üretim öncelikleri çelişkili          │
│    → Why 3: Yönetim güvenliği 2. planda tutuyor            │
│    → Why 4: Performans KPI'ları sadece üretim odaklı       │
│    → Why 5: Kök neden D4.1 (Güvenlik kültürü zayıf)        │
│                                                              │
│  • DAL 3: LOTO ihlali neden fark edilmedi?                  │
│    → Why 1: Süpervizör denetim yapmamış                     │
│    → Why 2: Denetim planı yok                               │
│    → Why 3: Sorumluluklar belirsiz                          │
│    → Why 4: Organizasyon yapısı karmaşık                    │
│    → Why 5: Kök neden D1.4 (İzleme eksikliği)              │
│                                                              │
│  Output:  part3 = {                                          │
│             analysis_branches: [3 dal],                      │
│             final_root_causes: [                             │
│               D3.2, D4.1, D1.4, (D1.5 opsiyonel)            │
│             ]                                                │
│           }                                                  │
│  Save:   outputs/electrical_shock_TIMESTAMP.json            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ ADIM 5: SkillBasedDocxAgent - LOTO Vurgusu                 │
│  Input:  {part1, part2, part3_rca}                          │
│  Process: OpenRouter Claude Sonnet 4.5                      │
│           • Özel vurgu: LOTO prosedürü eksiklikleri         │
│           • max_tokens: 32000                               │
│           • stream: False (hızlı ve güvenilir)              │
│           • temperature: 0.3                                │
│                                                              │
│  Output:  1. DOCX (18-20 sayfa):                            │
│              Bölüm 3: "Elektrik Güvenliği ve LOTO"          │
│              Bölüm 5: "LOTO Prosedür İhlali Analizi"        │
│              Bölüm 8: "LOTO Eğitim Önerileri"               │
│                                                              │
│           2. HTML (düzenlenebilir):                          │
│              Kırmızı vurgu: LOTO ihlalleri                  │
│              Turuncu: Eğitim gereklilikleri                 │
│              Yeşil: Düzeltici faaliyetler                   │
│                                                              │
│  Save:   outputs/INC-XXXXXXXX_electrical_shock.docx         │
│          outputs/INC-XXXXXXXX_electrical_shock.html         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ SONUÇ: LOTO Analizi Doğrulama                               │
│  ✅ RIDDOR: Y                                               │
│  ✅ Investigation Level: High                               │
│  ✅ Kök neden D3.2 (Eğitim) tespit edildi mi?               │
│  ✅ Kök neden D4.1 (Kültür) tespit edildi mi?               │
│  ✅ DOCX >50 KB                                             │
│  ✅ HTML >15 KB                                             │
│  → sys.exit(0) veya sys.exit(1)                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Beklenen Çıktılar

### 1. JSON Dosyası
**Dosya:** `outputs/electrical_shock_YYYYMMDD_HHMMSS.json`  
**Boyut:** ~18-22 KB  
**Özel İçerik:**
```json
{
  "analysis_branches": [
    {
      "branch_number": 1,
      "branch_title": "DAL 1 - LOTO PROSEDÜRÜ İHLALİ",
      "direct_cause_code": "A2.1",
      "direct_cause_title": "Prosedüre uymama",
      "why_chain": [
        {
          "number": 1,
          "question": "LOTO prosedürü neden uygulanmadı?",
          "answer": "Teknisyen LOTO eğitimi almamış",
          "code": "C"
        },
        ...
        {
          "number": 5,
          "question": "Eğitim ihtiyaçları neden belirlenmemiş?",
          "answer": "İK-HSE koordinasyonu ve yetkinlik matrisi yok",
          "code": "D"
        }
      ],
      "root_cause_code": "D3.2",
      "root_cause_title": "Eğitim ihtiyaçlarının belirlenmemesi"
    }
  ],
  "final_root_causes": [
    {
      "root_cause_code": "D3.2",
      "root_cause_category": "ORGANİZASYONEL",
      "root_cause_title": "Eğitim ihtiyaçlarının belirlenmemesi",
      "detailed_description": "LOTO yetkili çalışan eğitimi verilmemiş..."
    },
    {
      "root_cause_code": "D4.1",
      "root_cause_category": "ORGANİZASYONEL",
      "root_cause_title": "Güvenlik kültürü eksikliği",
      "detailed_description": "Üretim önceliği kültürü..."
    }
  ]
}
```

### 2. DOCX Raporu - LOTO Focused
**Dosya:** `outputs/INC-XXXXXXXX_electrical_shock.docx`  
**Boyut:** 52-62 KB  
**Özel Bölümler:**
- **Bölüm 3.2:** "Lockout/Tagout (LOTO) Prosedürü ve İhlalleri"
- **Bölüm 5.1:** "LOTO Eğitim Eksikliği Analizi"
- **Bölüm 7.1:** "Acil LOTO Eğitim Programı Önerisi"
- **Bölüm 8:** "Elektrik Güvenliği Kültürü Geliştirme"

### 3. HTML Raporu - Interactive
**Dosya:** `outputs/INC-XXXXXXXX_electrical_shock.html`  
**Boyut:** 16-21 KB  
**Özel Özellikler:**
- Kırmızı badge: "LOTO İHLALİ" vurguları
- Turuncu: Eğitim gereksinimleri
- Düzenlenebilir eğitim planı tablosu
- LOTO prosedür checklist

---

## ✅ Başarı Kriterleri

LOTO odaklı başarı kriterleri:

1. ✅ **RIDDOR: Y** (hospitalization)
2. ✅ **Investigation Level: High level**
3. ✅ **Kök neden D3.2** (LOTO Eğitimi) tespit edildi
4. ✅ **Kök neden D4.1** (Güvenlik Kültürü) tespit edildi
5. ✅ **Düzeltici faaliyet:** LOTO eğitim programı önerildi
6. ✅ **DOCX >50 KB** ve LOTO bölümleri var
7. ✅ **HTML >15 KB** ve düzenlenebilir

---

## 🚀 Çalıştırma

```bash
# Virtual environment
source .venv/bin/activate

# Test çalıştır
python test_electrical_shock.py

# LOTO analizi kontrol et
grep -i "LOTO\|lockout" outputs/electrical_shock_*.json

# Rapor kontrol
ls -lh outputs/INC-*electrical_shock.*
```

---

## 🐛 LOTO-Specific Sorun Giderme

### Sorun: LOTO kök nedeni tespit edilmedi
**Olası Neden:** AI "prosedür ihlali"ni insan hatası (A) olarak sınıfladı  
**Çözüm:** Prompt'ta "organizasyonel kök nedenlere odaklan" vurgusunu artırın

### Sorun: Güvenlik kültürü (D4.1) eksik
**Olası Neden:** Why zincirleri yeterince derine inmedi  
**Çözüm:** 5-Why'ın 5. seviyesine kadar gitmesini sağlayın

---

## 📚 LOTO Referanslar

- [OSHA 1910.147 LOTO Standard](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.147)
- [HSE LOTO Guidance](https://www.hse.gov.uk/pubns/indg253.pdf)
- [IEC 60204-1 Electrical Safety](https://webstore.iec.ch/)
- [NFPA 70E Electrical Safety](https://www.nfpa.org/70E)

---

## 🔗 İlgili Testler

- [Test: Yüksekten Düşme](./TEST_FALL_FROM_HEIGHT.md) - Prosedür ihlali karşılaştırması
- [Test: Makine Sıkışması](./TEST_MACHINE_ENTRAPMENT.md) - Güvenlik cihazı bypass

---

**Son Güncelleme:** 23 Şubat 2026  
**Versiyon:** 1.0  
**Özel Odak:** LOTO Prosedür Analizi  
**Yazar:** HSE RCA Test Sistemi

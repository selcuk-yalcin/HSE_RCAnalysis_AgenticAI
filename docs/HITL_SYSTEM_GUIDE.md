# 🔍 HSE HITL Question System - Comprehensive Guide

**Human-In-The-Loop Arayüzü ile Detaylı İş Kazası Root Cause Analizi**

## 🎯 SISTEM ÖZET

Bu sistem şu adımları izler:

```
┌─────────────────────────────────────────────────────────────┐
│ 1️⃣  KULLANICI OLAY AÇIKLAMASI GİRER (İlk/Kısıtlı Bilgi)    │
│    └─ "Elektrik çarpması oldu, hastaneye kaldırıldı"       │
│                                                             │
│ 2️⃣  SİSTEM ANALİZ EDER (OverviewAgent + AssessmentAgent)   │
│    └─ Olay tipi, şiddet, investigation level belirlenir   │
│                                                             │
│ 3️⃣  SORU SORMA YAPISI DEVREYE GİRER (Knowledge Base)        │
│    ├─ Eksik kategoriler tespit edilir                      │
│    ├─ HSG245 kodlarına bağlı sorular üretilir              │
│    └─ Gradio arayüzü ile sorular sunulur                   │
│                                                             │
│ 4️⃣  KULLANICI CEVAPLAR (Interactive Q&A)                    │
│    ├─ Her cevap kaydedilir                                 │
│    ├─ Takip soruları (5-Why) otomatik üretilir             │
│    └─ Detaylı bilgi toplanır                               │
│                                                             │
│ 5️⃣  ROOT CAUSE ANALYSIS (RootCauseAgentV2)                  │
│    ├─ Immediate causes belirlentr                          │
│    ├─ 5-Why zinciri ile inerken root causes bulunur        │
│    └─ Dallar halinde analiz yapılır                        │
│                                                             │
│ 6️⃣  RAPOR ÜRETİMİ (SkillBasedDocxAgent)                     │
│    ├─ DOCX rapor oluşturulur                               │
│    ├─ HTML rapor oluşturulur                               │
│    └─ JSON backup kaydedilir                               │
│                                                             │
│ 7️⃣  ÇIKTI: Kapsamlı İnceleme Raporu                         │
│    └─ Tüm kök nedenler, öneriler, HSG245 kodları           │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 ADIM ADIM AÇIKLAMA

### Adım 1: Olay Açıklaması (Initial Submission)

**Kullanıcı girer:**
```
"Bakım teknisyeni Kemal Arslan elektrik panosunda arıza giderme 
çalışması yaparken 380V yüksek voltaj akımına kapıldı. Teknisyen 
elektrik çarpması sonucu yere düştü ve bilinçsiz hale geldi."
```

**Sistem işler:**
1. `HybridInputProcessor`: Input analizi
   - Bilgi seviyesi: Level 3
   - Detail skoru: 0/13 (0% tamamlık)
   - Eksik kategoriler: 7 (kronoloji, prosedür, tanık, yönetim, ekipman, eğitim, ppe)

2. `OverviewAgent`: Olay tanımlama
   - Ref No: ELEC-2026-001
   - Olay Tipi: Electrical injury
   - Etkilenen: Kemal Arslan (29)
   - Yaralanma: Elektrik çarpması, yanık, kardiyak arrest

3. `AssessmentAgent`: Değerlendirme
   - Şiddet: Major
   - RIDDOR: Reportable - Yes
   - Investigation Level: High

**Çıktı:** Sorular hazırlanır

---

### Adım 2: Soru Sorma (Question Generation)

**Üretilen Sorular (Knowledge Base Entegre):**

```
KATEGORİ: Kronoloji
───────────────────────────────────────────────────────
1. [ZORUNLU] Olay hangi tarih ve saatte meydana geldi?
   → HSG245: A1.1, A1.2, A4.1, A4.2, A4.3
   
2. [OPSİYONEL] Olay öncesi son 2 saat içinde ne yapılıyordu?
   → HSG245: A4.1 (Yorgunluk), A4.2 (Dikkat dağınıklığı)

3. [OPSİYONEL] Olaydan sonuçlanmasına kadar geçen süre?
   → HSG245: A4.3 (Hızlı hareket), A5.3 (Acele etme)


KATEGORİ: Prosedür
───────────────────────────────────────────────────────
4. [ZORUNLU] Bu iş için yazılı bir prosedür/iş talimatı var mıydı?
   → HSG245: D4.1 (Prosedür yokluğu) vs A1.1 (Prosedür ihlali)

5. [ZORUNLU] Prosedür sahada uygulanabilir miydi?
   → HSG245: A1.6 (Uygulanamaz prosedür) vs A1.8 (Gerçekçi olmayan varsayımlar)

6. [ZORUNLU] Çalışan bu prosedürü biliyor muydu?
   → HSG245: D3.1 (Yetersiz eğitim) vs A1.1 (Bilinçli ihlal)


KATEGORİ: Yönetim
───────────────────────────────────────────────────────
7. [ZORUNLU] Bu iş için gözetim/denetim planlandı mı?
   → HSG245: D1.1 (Yetersiz liderlik), D7.1 (Organizasyon eksikliği)

8. [ZORUNLU] Yönetim bu riski biliyor muydu?
   → HSG245: D1.9 (Göz yumma), D1.4 (Yanlış önceliklendirme)

...
```

**Sistem Logic:**
- Eksik kategorilere göre sorular seçilir
- Her soru HSG245 kodlarına bağlantılıdır
- Zorunlu ve opsiyonel sorular ayırımı yapılır
- Sorular bilgi seviyesine göre uyarlanır

---

### Adım 3: Kullanıcı Cevaplar (Q&A Loop)

**Kullanıcı cevaplar:**
```
S: Bu iş için yazılı bir prosedür/iş talimatı var mıydı?
C: LOTO (Lockout/Tagout) prosedürü vardır, ancak uygulanmıyor.
   Personel prosedürü bilir ancak "Üretim durmasın" baskısı 
   nedeniyle uygulamıyor.
```

**Sistem otomatik takip soruları üretir (5-Why):**
```
🔄 TAKIP SORULARI (5-Why)

1. Neden uygulanmıyor?
   → HSG245: D1.9 (Göz yumma)
   → Why Level: 2

2. Neden "Üretim durmasın" baskısı var?
   → HSG245: D1.4 (Yanlış önceliklendirme)
   → Why Level: 2

3. Yönetim neden güvenlik yerine üretimi önceliklendirir?
   → HSG245: D1.1 (Yetersiz liderlik), D7.2 (Kaynak eksikliği)
   → Why Level: 3
```

**Cevap Analizi:**
- Cevap kaydedilir
- Anahtar kelimeler çıkarılır
- 5-Why zincirinin bir seviyesi ileriye gidilir
- Takip soruları otomatik üretilir
- Sonraki soru önerilir

---

### Adım 4: Root Cause Analysis (RCA)

**RootCauseAgentV2 işlemi:**

```
📊 ROOT CAUSE ANALYSIS SONUÇLARI

🌿 DAL 1: PROSEDÜREL HASAR (Procedural Failure)
─────────────────────────────────────────────────────
  Immediate Cause: [A1.1] LOTO prosedürü uygulanmadı
  
  Why #1: Neden LOTO uygulanmıyor?
    → Cevap: "Üretim duracak diye..."
    → Kod: D1.9 (Göz yumma)
    
  Why #2: Neden "üretim duracak" kaygısı?
    → Cevap: "Yönetim üretim hedefini koydu"
    → Kod: D1.4 (Yanlış önceliklendirme)
    
  Why #3: Neden yönetim öyle hareket ediyor?
    → Cevap: "Güvenlik kültürü yok"
    → Kod: D1.1 (Yetersiz liderlik)
    
  Why #4: Neden güvenlik kültürü kurulmamış?
    → Cevap: "Sistemik sorun, risk normalleşmiş"
    → Kod: D7.2 (Uygun kaynak tahsisi eksikliği)
  
  🎯 ROOT CAUSE: [D1.1] Yetersiz Güvenlik Liderliği
                 + [D7.2] Sistemik Organizasyon Eksikliği


🌿 DAL 2: EĞİTİM HASAR (Training Failure)
─────────────────────────────────────────────────────
  Immediate Cause: [D3.1] LOTO eğitimi 2 yıl önce verilmiş (tekrar yok)
  
  Why #1: Neden tekrar eğitim yapılmıyor?
    → Cevap: "Periyodik eğitim sistemi yok"
    → Kod: D3.3 (Eğitim takibi eksikliği)
    
  Why #2: Neden sistem yok?
    → Cevap: "İK tarafından denetlenmiyor"
    → Kod: D7.1 (Organizasyon eksikliği)
  
  🎯 ROOT CAUSE: [D3.3] Periyodik Eğitim Eksikliği
                 + [D7.1] Systemik Denetim Eksikliği


🌿 DAL 3: DENETİM HASAR (Supervision Failure)
─────────────────────────────────────────────────────
  Immediate Cause: [D1.5] Gözetim/denetim yapılmıyor
  
  Why #1: Neden denetim yapılmıyor?
    → Cevap: "Bakım işleri düzenli denetlenmiyor"
    → Kod: D7.3 (Denetim eksikliği)
    
  Why #2: Neden sistem oluşturulmamış?
    → Cevap: "Kaynak yetersiz"
    → Kod: D7.2 (Kaynak tahsisi eksikliği)
  
  🎯 ROOT CAUSE: [D7.3] Sistemik Denetim Eksikliği


════════════════════════════════════════════════════════
🎯 ÖZET KÖK NEDENLER (Priority Order):
════════════════════════════════════════════════════════

1. [D1.1] Yetersiz Güvenlik Liderliği
   → LOTO yok olsa bile iş güvenliği kültürü oluşturmalı

2. [D7.2] Sistemik Organizasyon Eksikliği  
   → Periyodik denetim, eğitim sistemi gerekli

3. [D3.3] Periyodik Eğitim Eksikliği
   → 2 yıl eski eğitim yeterli değil

4. [D1.5] Gözetim/Denetim Eksikliği
   → İkinci kişi kontrolü, sahra denetimi yok

5. [D4.1] Prosedür Uygulanmama
   → Prosedür var, ama kâğıt üzerinde
```

**Çıktı:** 3-4 dal, 5+ root cause belirlenir

---

### Adım 5: Rapor Üretimi

**SkillBasedDocxAgent ile üretilen rapor:**

```
📄 COMPREHENSIVE REPORT

1. OLAY ÖZETİ
   • Ref No: ELEC-2026-001
   • Tarih: 20 Şubat 2026
   • Konum: Üretim Tesisi - MDB-02
   • Etkilenen: Kemal Arslan (29)
   • Sonuç: Major Injury + RIDDOR Reportable

2. YARALANMA DETAYLARı
   • Tip: Electrical Shock (380V, 3-phase)
   • Severity: Kardiyak arrest, 2nd degree burns
   • İşe Dönüş: 3 ay sonra

3. ROOT CAUSE ANALYSIS
   DAL 1: Prosedürel Hasar
   DAL 2: Eğitim Eksikliği
   DAL 3: Denetim Eksikliği

4. KÖK NEDENLER
   1. Yetersiz Güvenlik Liderliği [D1.1]
   2. Sistemik Organizasyon Eksikliği [D7.2]
   3. Periyodik Eğitim Eksikliği [D3.3]
   4. Gözetim/Denetim Eksikliği [D1.5]

5. ÖNERİLEN AKSIYONLAR
   1. LOTO Zorunlu Hale Getir
      → Timeline: Hafta 1
      → Sorumlu: Bakım Müdürü
      
   2. Periyodik Eğitim Sistemi
      → Timeline: Ay 1-3
      → Sorumlu: İK Müdürü
      
   3. Denetim Sistemi Oluştur
      → Timeline: Ay 1-6
      → Sorumlu: Güvenlik Müdürü
      
   4. Güvenlik Kültürü Projesi
      → Timeline: Devam eden
      → Sorumlu: Yönetim

6. HSG245 CODE MAPPING
   A1.1 → LOTO Prosedürü İhlali
   D1.1 → Yetersiz Liderlik
   D3.3 → Eğitim Eksikliği
   D7.2 → Organizasyon Eksikliği
   ...

RAPORLAR: 
  • DOCX: /outputs/ELEC-2026-001_20260302_120000.docx
  • HTML: /outputs/ELEC-2026-001_20260302_120000.html
  • JSON: /outputs/ELEC-2026-001_20260302_120000.json
```

---

## 🚀 ÇALIŞTIRILMESI

### Gradio Arayüzü ile

```bash
# Proje root'unda
cd /Users/selcuk/Desktop/HSE_RCAnalysis_AgenticAI-main

# Aktivasyon
source .venv/bin/activate

# Gradio uygulamasını başlat
python hitl_test/gradio_hitl_system.py

# Browser'da açılır: http://127.0.0.1:7860
```

### Arayüz Kullanımı

1. **Adım 1:** "Olay Açıklaması" metin alanına kazayı anlatın
2. **Adım 2:** "✅ Olay Analizini Başlat" butonuna tıklayın
3. **Adım 3:** Sorular otomatik yüklenecek
4. **Adım 4:** Soru numarası seçin, cevaplayın, "✅ Cevap Gönder" tıklayın
5. **Adım 5:** Takip soruları otomatik üretilecek
6. **Adım 6:** Tüm sorular cevaplanınca "▶️ RCA Analizi Başlat" tıklayın
7. **Adım 7:** Root causes belirlenecek
8. **Adım 8:** "📊 Rapor Üret" tıklayın
9. **Adım 9:** DOCX + HTML raporlar `/outputs/` klasöründe oluşturulur

---

## 📊 SYSTEM FLOW DIAGRAM

```
┌──────────────────────────────────────────┐
│   USER ENTERS INCIDENT DESCRIPTION       │
│   "Elektrik çarpması oldu..."            │
└──────────────────┬───────────────────────┘
                   │
                   ▼
       ┌─────────────────────────────────────┐
       │ HybridInputProcessor                │
       │ └─ Bilgi seviyesi: Level 3          │
       │ └─ Detail skoru: 0/13               │
       │ └─ Eksik: 7 kategori               │
       └──────────────┬──────────────────────┘
                      │
                      ▼
       ┌──────────────────────────────────────────┐
       │ OverviewAgent                            │
       │ └─ Ref No: ELEC-2026-001                 │
       │ └─ Incident Type: Electrical Injury      │
       │ └─ Affected: Kemal Arslan                │
       └──────────────┬───────────────────────────┘
                      │
                      ▼
       ┌──────────────────────────────────────────┐
       │ AssessmentAgent                          │
       │ └─ Severity: Major                       │
       │ └─ RIDDOR: Yes                           │
       │ └─ Investigation: High                   │
       └──────────────┬───────────────────────────┘
                      │
                      ▼
       ┌──────────────────────────────────────────┐
       │ QuestionEngine (Knowledge Base)          │
       │ └─ Generate 30+ sorular                  │
       │ └─ HSG245 kodlarına bağla                │
       │ └─ Gradio'da göster                      │
       └──────────────┬───────────────────────────┘
                      │
                      ▼
    ┌─────────────────────────────────────────┐
    │   USER ANSWERS QUESTIONS (Interactive)   │
    │   SYSTEM CREATES 5-WHY FOLLOW-UPS       │
    └──────────────┬────────────────────────────┘
                   │
                   ▼
       ┌──────────────────────────────────────────┐
       │ RootCauseAgentV2                         │
       │ └─ Immediate causes: 3-4                 │
       │ └─ 5-Why chain: 4-5 levels               │
       │ └─ Root causes: 5-7 adet                 │
       │ └─ Branches: 3-4                         │
       └──────────────┬───────────────────────────┘
                      │
                      ▼
       ┌──────────────────────────────────────────┐
       │ SkillBasedDocxAgent                      │
       │ └─ Generate DOCX Report                  │
       │ └─ Generate HTML Report                  │
       │ └─ Save JSON Backup                      │
       └──────────────┬───────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────────────┐
        │ OUTPUT FILES IN /outputs/                │
        │ ├─ DOCX Report (30-50 pages)            │
        │ ├─ HTML Report (viewable in browser)    │
        │ └─ JSON Data (backup)                   │
        └─────────────────────────────────────────┘
```

---

## 🎓 ÖRNEK SENARYO

### Input
```
"Bakım teknisyeni Kemal Arslan (29) elektrik panosunda arıza giderme 
çalışması yaparken 380V yüksek voltaj akımına kapıldı. Teknisyen 
elektrik çarpması sonucu yere düştü ve bilinçsiz hale geldi."
```

### System Output
```
✅ Olay Tahlili
  Ref: ELEC-2026-001
  Tip: Electrical Injury
  Şiddet: Major
  RIDDOR: Yes
  
❓ Sorular (30 adet)
  1. Olay tarihi ve saati?
  2. Prosedür var mıydı?
  3. LOTO uygulandı mı?
  ... (27 soru daha)

📊 Root Causes (5 adet)
  1. [D1.1] Yetersiz Güvenlik Liderliği
  2. [D7.2] Organizasyon Eksikliği
  3. [D3.3] Eğitim Eksikliği
  4. [D1.5] Gözetim Eksikliği
  5. [D4.1] Prosedür Uygulanmama

📄 Raporlar
  • /outputs/ELEC-2026-001_20260302_120000.docx
  • /outputs/ELEC-2026-001_20260302_120000.html
  • /outputs/ELEC-2026-001_20260302_120000.json
```

---

## 🔄 İteratif Process (Human-in-the-Loop)

```
ITERATION 1:
  ├─ Soru: Prosedür var mıydı?
  ├─ Cevap: "Var ama uygulanmıyor"
  └─ Follow-up: Neden uygulanmıyor?

ITERATION 2:
  ├─ Soru: Neden uygulanmıyor?
  ├─ Cevap: "Üretim durmasın diye"
  └─ Follow-up: Yönetim neden öyle düşünüyor?

ITERATION 3:
  ├─ Soru: Yönetim neden öyle?
  ├─ Cevap: "Güvenlik kültürü yok, üretim hedefi var"
  └─ Follow-up: Kültür neden yoksa?

ITERATION 4:
  ├─ Soru: Kültür neden oluşturulmadı?
  ├─ Cevap: "Sistem eksik, denetim yok"
  └─ ROOT CAUSE: Sistemik Organizasyon Eksikliği [D7.2]
```

Her iterasyonda:
- ✅ Cevap kaydedilir
- ✅ Anahtar bilgiler çıkarılır
- ✅ Takip soruları otomatik üretilir
- ✅ Detay derinleştirilir
- ✅ Root cause yaklaşılır

---

## 🛠️ TECHNICAL COMPONENTS

| Bileşen | Rolü | Input | Output |
|---------|------|-------|--------|
| **HybridInputProcessor** | Input analizi | Metin | Level, Detail, Eksik kategoriler |
| **OverviewAgent** | Olay tanımlama | Input | Part1 (Ref, Tip, Kişi, Yaralanma) |
| **AssessmentAgent** | Değerlendirme | Part1 | Part2 (Şiddet, RIDDOR, Level) |
| **QuestionEngine** | Soru üretimi | Eksik kategoriler | Soru listesi (HSG245 entegre) |
| **RootCauseAgentV2** | RCA analizi | Part1, Part2, Cevaplar | Part3 (Dallar, Root causes) |
| **SkillBasedDocxAgent** | Rapor üretimi | Part1, Part2, Part3 | DOCX + HTML Raporlar |
| **Gradio Interface** | Kullanıcı arayüzü | Input, Cevaplar | Sorular, Sonuçlar, Rapor |

---

## 📈 SİSTEM ÖZELLİKLERİ

✅ **Automated Question Generation** - Knowledge Base entegre  
✅ **Interactive Q&A Loop** - İnsan-makine etkileşimi  
✅ **5-Why Automation** - Takip soruları otomatik  
✅ **HSG245 Integration** - Tüm sorular kodla bağlı  
✅ **Multi-Branch RCA** - Paralel analiz dalları  
✅ **Comprehensive Reporting** - DOCX + HTML çıktı  
✅ **Real-time Processing** - Anlık soru ve cevap  
✅ **User-Friendly UI** - Gradio arayüzü  

---

## 📞 SUPPORT

**Sorular?**
- Sistem akışı: Bak `FLOW DIAGRAM`
- Soru üretimi: Bak `QUESTION_ENGINE.md`
- RCA detayları: Bak `ROOT_CAUSE_AGENT.md`
- Rapor özelleştirmesi: Bak `SKILLBASED_DOCX.md`

**Özelleştirmeler:**
- Sorular değiştirebilirsiniz: `/agents/question_engine.py`
- Raporları özelleştirebilirsiniz: `/agents/skillbased_docx_agent.py`
- Workflow değiştirebilirsiniz: `gradio_hitl_system.py`

---

**Son Güncelleme:** 2 Mart 2026  
**Durum:** ✅ HAZIR KULLANIM


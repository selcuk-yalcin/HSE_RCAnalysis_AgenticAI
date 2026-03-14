# HITL Hybrid System - Detaylı Tasarım Belgesi

## 📋 Genel Bakış

Bu belge, **Human-in-the-Loop (HITL)** kök neden analizi sisteminin **hibrit** versiyonunun detaylı tasarımını içerir. Sistem, kullanıcının **ne kadar detay vermek istediğine** göre esnek çalışır:

- **Senaryo 1**: Kullanıcı tüm bilgileri baştan verir → AI direkt analiz yapar
- **Senaryo 2**: Kullanıcı kısmi bilgi verir → AI eksikleri sorar ve tamamlatır
- **Senaryo 3**: Kullanıcı sadece olay özetini verir → AI adım adım sorgular ve birlikte analiz yapar

---

## 🎯 Sistem Prensipleri

### 1. Esnek Giriş Modeli
```
Kullanıcı Girişi (3 Seviye):

┌──────────────────────────────────────────────────────┐
│ SEVİYE 1: DETAYLI RAPOR (Test formatı)              │
│ • Olay kronolojisi                                   │
│ • Tanık beyanları                                    │
│ • Prosedür ihlalleri                                 │
│ • Kök neden ön bulguları                             │
│ → AI: Direkt kök neden analizi yapar                │
└──────────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────────┐
│ SEVİYE 2: ORTA DETAY (Yapılandırılmış form)         │
│ • Olay özeti                                         │
│ • Yaralanan kişi bilgisi                             │
│ • Temel güvenlik ihlalleri                           │
│ → AI: Eksikleri sorar (prosedür var mıydı? vb.)    │
└──────────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────────┐
│ SEVİYE 3: MİNİMAL (Serbest metin)                   │
│ • Sadece olay özeti (1-2 paragraf)                   │
│ → AI: Tüm detayları adım adım sorar                 │
└──────────────────────────────────────────────────────┘
```

### 2. Akıllı Detay Tespiti
AI, kullanıcı girdisini analiz eder ve **hangi bilgilerin eksik** olduğunu tespit eder:

```python
Örnek Girdi: "Forklift geri manevra yaparken çalışana çarptı."

AI Eksiklik Tespiti:
✗ Prosedür ihlali bilgisi yok → Sor
✗ Ekipman durumu bilgisi yok → Sor  
✗ Tanık beyanı yok → Sor
✗ Yönetimsel faktör yok → Sor
✓ Olay tipi belli → Direk analiz et
```

### 3. Bağlamsal Sorgulama
AI, **olay tipine göre** özelleşmiş sorular sorar:

| Olay Tipi | Özel Sorgular |
|-----------|---------------|
| Elektrik | LOTO uygulandı mı? Test edildi mi? PPE var mıydı? |
| Düşme | Korkuluk var mıydı? Emniyet kemeri takılı mıydı? Risk değerlendirmesi yapılmış mıydı? |
| Forklift | İkaz sistemi çalışıyor muydu? Sürücü yetkili miydi? Hız limiti var mıydı? |
| Kimyasal | SDS mevcut muydu? Havalandırma yeterliydi mi? Acil duş var mıydı? |

---

## 🏗️ Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────────────┐
│                     GRADIO ARAYÜZÜ                              │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ TAB 1: OLAY GİRİŞİ (Esnek Format)                      │    │
│  │ • Serbest metin alanı                                   │    │
│  │ • Yapılandırılmış form (opsiyonel)                      │    │
│  │ • Test formatı şablon (upload)                          │    │
│  └────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ TAB 2: EKSİK BİLGİ TAMAMLAMA (AI Sorgulaması)         │    │
│  │ • AI'nın tespit ettiği eksiklikler                      │    │
│  │ • Çoktan seçmeli veya açık uçlu sorular                │    │
│  │ • "Atla" seçeneği (AI tahmini kullan)                  │    │
│  └────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ TAB 3: KÖK NEDEN ONAY (Kod Seçimi)                     │    │
│  │ • AI önerisi + manuel düzeltme                          │    │
│  │ • Dal bazında onayla/reddet                             │    │
│  └────────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────────┐    │
│  │ TAB 4: RAPOR ÖNİZLEME                                   │    │
│  │ • DOCX/HTML/JSON indirme                                │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              HYBRID INPUT PROCESSOR                             │
│  - Girdi seviyesini tespit eder (Level 1/2/3)                  │
│  - Eksik alanları listeler                                      │
│  - Sorgulama stratejisini belirler                             │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              INTELLIGENT QUESTION ENGINE                        │
│  - Knowledge base'den bağlamsal sorular üretir                 │
│  - Olay tipine göre özelleştirir                               │
│  - Dallanma mantığı (if-then)                                  │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   AI AGENTS (Mevcut)                            │
│  OverviewAgent → AssessmentAgent → RootCauseAgentV2            │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 APPROVAL & CORRECTION LOOP                      │
│  - Kod önerileri                                                │
│  - Manuel düzeltme                                              │
│  - Düzeltici faaliyet önerileri                                │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   REPORT GENERATION                             │
│  SkillBasedDocxAgent → DOCX + HTML + JSON                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📝 Örnek Senaryolar

### **SENARYO 1: Detaylı Rapor (Test Formatı)**

#### Kullanıcı Girişi:
```
INCIDENT_DATA = """
OLAY RAPORU - ELEKTRİK ÇARPMASI

Tarih: 20 Şubat 2026, Saat: 15:20
Lokasyon: Üretim Tesisi - Ana Elektrik Panosu (MDB-02)
Rapor Eden: Elektrik Bakım Sorumlusu - İbrahim Aydın

OLAY AÇIKLAMASI:
Bakım teknisyeni Kemal Arslan (29) elektrik panosunda arıza giderme 
çalışması yaparken 380V yüksek voltaj akımına kapıldı.

LOTO (LOCKOUT/TAGOUT) PROSEDÜRÜ:
❌ UYGULANMADI
- Prosedür dokümanı: VAR (ancak uygulanmıyor)
- LOTO kitleri: Depoda mevcut (kullanılmıyor)

KÖK NEDEN ÖN BULGULAR:
1. LOTO prosedürü kâğıt üzerinde var, pratikte uygulanmıyor
2. "Üretim durmasın" baskısı - enerji kesme korkusu

TANIK BEYANLARI:
- Ali Yılmaz (Teknisyen): "Kemal acele ediyordu. Üretim duracak diye 
  enerjiyi kesmedi. Hep böyle yapıyoruz aslında."
"""
```

#### Sistem Aksiyon:
```
┌────────────────────────────────────────────────────────┐
│ 🤖 AI ANALİZ SONUCU                                    │
├────────────────────────────────────────────────────────┤
│ ✅ Yeterli detay mevcut!                               │
│                                                         │
│ Tespit Edilen Bilgiler:                                │
│ ✓ Olay kronolojisi                                     │
│ ✓ Prosedür ihlali (LOTO)                               │
│ ✓ Tanık beyanı                                         │
│ ✓ Kök neden ön bulgusu                                 │
│                                                         │
│ Direkt kök neden analizine geçiliyor...                │
│                                                         │
│ [Analize Başla →]                                      │
└────────────────────────────────────────────────────────┘
```

**AI İşlemi:**
- Eksik bilgi sorgulaması YOK
- Direkt `RootCauseAgentV2` çalışır
- Kod önerileri üretilir
- Kullanıcı sadece onay verir

---

### **SENARYO 2: Orta Detay (Yapılandırılmış Form)**

#### Kullanıcı Girişi (Gradio Form):
```
┌────────────────────────────────────────────────────────┐
│ 📋 OLAY BİLGİLERİ FORMU                                │
├────────────────────────────────────────────────────────┤
│ Olay Tipi: [Elektrik Çarpması ▼]                      │
│                                                         │
│ Olay Özeti:                                            │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Teknisyen elektrik panosunda çalışırken 380V       │ │
│ │ akımına kapıldı. Hastaneye kaldırıldı.             │ │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
│ Yaralanan Kişi:                                        │
│ Ad Soyad: [Kemal Arslan      ]                        │
│ Yaş: [29]  Deneyim: [4 yıl   ]                        │
│                                                         │
│ Temel Güvenlik İhlalleri:                              │
│ ☑ LOTO uygulanmadı                                     │
│ ☑ PPE kullanılmadı                                     │
│ ☐ İş izni alınmadı                                     │
│                                                         │
│ [İlerle →]                                             │
└────────────────────────────────────────────────────────┘
```

#### AI Eksiklik Tespiti:
```
┌────────────────────────────────────────────────────────┐
│ 🔍 EKSİK BİLGİ TESPİTİ                                 │
├────────────────────────────────────────────────────────┤
│ AI Analizi:                                            │
│ "LOTO uygulanmadı" ihlali tespit edildi.              │
│                                                         │
│ Eksik bilgiler:                                        │
│ ❓ LOTO prosedürü var mıydı?                           │
│ ❓ LOTO eğitimi verilmiş miydi?                        │
│ ❓ Amir/yönetim neden müdahale etmedi?                 │
│                                                         │
│ Bu bilgileri tamamlamak için 3 soru soracağım.         │
│                                                         │
│ [Soruları Başlat →]  [Atla (AI Tahmini) ⏭]           │
└────────────────────────────────────────────────────────┘
```

#### AI Sorgulama Başlar:
```
┌────────────────────────────────────────────────────────┐
│ ❓ SORU 1/3: LOTO Prosedürü                            │
├────────────────────────────────────────────────────────┤
│ "LOTO prosedürü şirkette mevcut muydu?"                │
│                                                         │
│ ○ Hayır, LOTO prosedürü hiç yoktu                      │
│   → [D4.1] Prosedür mevcut değil                       │
│                                                         │
│ ● Evet, prosedür vardı ama uygulanmıyordu             │
│   → [D4.2] Prosedür var ama uygulanmıyor              │
│                                                         │
│ ○ Prosedür vardı ve uygulanıyordu, bu sefer atlandı   │
│   → [A1.1] Bireysel kural ihlali                      │
│                                                         │
│ Ek açıklama (opsiyonel):                               │
│ ┌────────────────────────────────────────────────────┐ │
│ │ LOTO prosedürü dokümanda var ama üretim baskısı   │ │
│ │ nedeniyle hiç uygulanmıyor.                        │ │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
│ [← Geri]  [İlerle →]  [Atla ⏭]                       │
└────────────────────────────────────────────────────────┘
```

**Dallanma Mantığı:**
```
LOTO prosedürü var mıydı?
├─ HAYIR → [D4.1] Prosedür yok
│          → SORU 2: "Neden prosedür oluşturulmamış?"
│             ├─ Bilgi eksikliği → [D4.1]
│             └─ Bütçe/kaynak eksik → [D6.2]
│
└─ EVET → SORU 1B: "Prosedür uygulandı mı?"
          ├─ HAYIR → [D4.2] veya [D1.9]
          │          → SORU 2: "Neden uygulanmadı?"
          │             ├─ Eğitim eksikliği → [D3.1]
          │             ├─ Zaman baskısı → [D1.4]
          │             └─ Yönetim toleransı → [D1.9]
          │
          └─ EVET (genelde) → [A1.1] Bireysel ihlal
                     → SORU 2: "Neden bu sefer atladı?"
                        ├─ Unuttu → [C2.1]
                        └─ Acele etti → [A4.8]
```

---

### **SENARYO 3: Minimal Giriş (Serbest Metin)**

#### Kullanıcı Girişi:
```
┌────────────────────────────────────────────────────────┐
│ 📝 OLAY AÇIKLAMASI                                     │
├────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────────────┐ │
│ │ Forklift geri manevra yaparken yaya yolundaki     │ │
│ │ çalışana çarptı. Çalışan ayağından yaralandı.     │ │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
│ [Analize Başla →]                                      │
└────────────────────────────────────────────────────────┘
```

#### AI İlk Analiz:
```
┌────────────────────────────────────────────────────────┐
│ 🤖 İLK ANALİZ                                          │
├────────────────────────────────────────────────────────┤
│ Tespit Edilen:                                         │
│ • Olay Tipi: Araç kazası (Forklift)                   │
│ • Yaralanma: Muhtemelen ciddi                          │
│ • Konum: Yaya yolu                                     │
│                                                         │
│ Eksik Bilgiler (çok):                                  │
│ ❓ Forklift ikaz sistemi (geri vites sesi)            │
│ ❓ Sürücü yetkilendirmesi                              │
│ ❓ Yaya yolu işaretleme                                │
│ ❓ Hız limiti/kural                                    │
│ ❓ Gözetim durumu                                      │
│                                                         │
│ 8-10 soru ile detaylı analiz yapabiliriz.              │
│                                                         │
│ [Detaylı Sorgulamaya Başla →]                          │
│ [Hızlı Analiz Yap (AI Tahmini) ⏭]                    │
└────────────────────────────────────────────────────────┘
```

#### Adım Adım Sorgulama:
```
┌────────────────────────────────────────────────────────┐
│ ❓ SORU 1/8: Fiziksel Koşul                            │
├────────────────────────────────────────────────────────┤
│ "Forkliftin geri vites ikaz sistemi çalışıyor muydu?" │
│                                                         │
│ ○ Evet, çalışıyordu                                    │
│   → [A4.1] Dikkat dağınıklığı olabilir                │
│                                                         │
│ ● Hayır, arızalıydı                                    │
│   → [B1.5] Uyarı/alarm arızası                        │
│                                                         │
│ ○ Bilmiyorum                                           │
│   → AI tahmini kullanılır                              │
│                                                         │
│ [İlerle →]                                             │
└────────────────────────────────────────────────────────┘
```

**Kullanıcı Cevabı:** "Hayır, arızalıydı"

```
┌────────────────────────────────────────────────────────┐
│ ❓ SORU 2/8: Bakım/Kontrol                             │
├────────────────────────────────────────────────────────┤
│ "Bu arıza vardiya öncesi kontrollerde fark edildi mi?" │
│                                                         │
│ ○ Evet, fark edildi ama bilerek kullanıldı            │
│   → [A2.3] Arızalı ekipman kullanımı                  │
│                                                         │
│ ● Hayır, kontrol yapılmadı                             │
│   → [B2.2] Yetersiz ekipman hazırlığı                 │
│                                                         │
│ ○ Kontrol yapıldı ama arıza tespit edilemedi          │
│   → [B2.7] Gizli kusur                                │
│                                                         │
│ [İlerle →]                                             │
└────────────────────────────────────────────────────────┘
```

**Kullanıcı Cevabı:** "Hayır, kontrol yapılmadı"

```
┌────────────────────────────────────────────────────────┐
│ ❓ SORU 3/8: İnsan Faktörü                             │
├────────────────────────────────────────────────────────┤
│ "Vardiya kontrol formu neden doldurulmadı?"            │
│                                                         │
│ ○ Sürücü unuttu / bilmiyordu                           │
│   → [C2.1] Hafıza kısıtlaması veya [D3.1] Eğitim     │
│                                                         │
│ ● Zaman baskısı vardı, acele etti                      │
│   → [A4.8] Zaman baskısı                              │
│                                                         │
│ ○ Hep böyle yapılıyor, normalleşmiş                    │
│   → [D1.5] Sapma normalleşmesi                        │
│                                                         │
│ Açıklama:                                              │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Depoda yoğun sevkiyat vardı, şef "hızlı olun,     │ │
│ │ formları sonra hallederiz" dedi.                   │ │
│ └────────────────────────────────────────────────────┘ │
│                                                         │
│ [İlerle →]                                             │
└────────────────────────────────────────────────────────┘
```

**Sistem:** Açıklamadan "şef" kelimesini yakalar → Yönetimsel faktör (D) kategorisine geçer

```
┌────────────────────────────────────────────────────────┐
│ ❓ SORU 4/8: Yönetimsel Faktör (KÖK NEDEN)            │
├────────────────────────────────────────────────────────┤
│ "Şefin formu atlatması hangi kök nedeni gösterir?"    │
│                                                         │
│ ● D1.4: Üretim baskısının güvenliğin önüne geçmesi    │
│   (Sevkiyat hedefleri > güvenlik)                      │
│                                                         │
│ ○ D1.5: Sapmaların normalleşmesi                       │
│   (Form atlama "hep böyle" yapılıyor)                  │
│                                                         │
│ ○ D1.2: Yetersiz gözetim                               │
│   (Şef denetim yapmıyor)                               │
│                                                         │
│ ○ D1.9: Yönetimin bilinen sapmalara toleransı         │
│   (Şef ihlali biliyor, müdahale etmiyor)              │
│                                                         │
│ [Kök Nedeni Onayla →]                                  │
└────────────────────────────────────────────────────────┘
```

**Kullanıcı Seçimi:** D1.4

**Sistem:** 5-Why zinciri tamamlandı!

```
┌────────────────────────────────────────────────────────┐
│ ✅ KÖK NEDEN ANALİZİ TAMAMLANDI                        │
├────────────────────────────────────────────────────────┤
│ DAL 1: Forklift İkaz Sistemi Arızası                   │
│                                                         │
│ ❓ Neden 1? → [B1.5] İkaz sistemi arızalıydı          │
│ ❓ Neden 2? → [B2.2] Vardiya kontrolü yapılmadı       │
│ ❓ Neden 3? → [A4.8] Zaman baskısı (şef acele etti)   │
│ 🎯 KÖK NEDEN → [D1.4] Üretim > Güvenlik               │
│                                                         │
│ Kanıt:                                                 │
│ "Şef: 'Hızlı olun, formları sonra hallederiz'"       │
│                                                         │
│ [Düzeltici Faaliyetlere Geç →]                         │
└────────────────────────────────────────────────────────┘
```

---

## 🔧 Teknik Uygulama

### **1. Dosya Yapısı**

```
HSE_RCAnalysis_AgenticAI-main/
│
├── hitl/                              # YENİ KLASÖR
│   ├── __init__.py
│   ├── gradio_app.py                  # Ana Gradio arayüzü
│   ├── hybrid_input_processor.py      # Girdi seviyesi tespit
│   ├── question_engine.py             # Soru üretim motoru
│   ├── code_selector.py               # HSG245 kod seçimi
│   ├── approval_handler.py            # Onay/düzeltme döngüsü
│   └── templates/
│       ├── incident_form_template.txt # Yapılandırılmış form şablonu
│       └── test_format_template.txt   # Test formatı şablonu
│
├── agents/
│   ├── overview_agent.py
│   ├── assessment_agent.py
│   ├── rootcause_agent_v2.py
│   ├── skillbased_docx_agent.py
│   └── knowledge_base.py              # HSG245 taksonomi
│
├── tests/
│   ├── test_electrical_shock 2.py     # Detaylı test örneği
│   ├── test_hitl_minimal.py           # Minimal giriş testi
│   └── test_hitl_hybrid.py            # Hibrit akış testi
│
└── docs/
    ├── HITL_HYBRID_DESIGN.md          # Bu belge
    └── HITL_USER_GUIDE.md             # Kullanıcı kılavuzu
```

---

### **2. `hybrid_input_processor.py` - Girdi Seviyesi Tespit**

**Amaç:** Kullanıcı girdisini analiz ederek ne kadar bilgi verildiğini tespit eder.

```python
"""
Hybrid Input Processor - Girdi Seviyesi Tespiti
"""

from typing import Dict, List, Tuple
import re


class HybridInputProcessor:
    """
    Kullanıcı girdisini analiz eder ve eksiklikleri tespit eder.
    """
    
    # Anahtar kelime setleri (detay göstergesi)
    KEYWORDS = {
        "kronoloji": ["saat", "tarih", "zaman", "kronoloji", "timeline"],
        "prosedür": ["prosedür", "procedure", "LOTO", "iş izni", "permit"],
        "tanik": ["tanık", "witness", "beyan", "statement", "ifade"],
        "yönetim": ["yönetim", "management", "baskı", "pressure", "kültür"],
        "ekipman": ["ekipman", "equipment", "arıza", "failure", "bakım"],
        "eğitim": ["eğitim", "training", "sertifika", "certificate"],
        "ppe": ["KKD", "PPE", "eldiven", "glove", "baret", "helmet"],
    }
    
    def __init__(self):
        pass
    
    def detect_input_level(self, incident_text: str) -> Tuple[int, Dict]:
        """
        Girdi seviyesini tespit eder.
        
        Returns:
            (level, details)
            - level: 1 (detaylı), 2 (orta), 3 (minimal)
            - details: {
                "present": [...],  # Mevcut bilgiler
                "missing": [...],  # Eksik bilgiler
                "keywords_found": {...}
              }
        """
        text_lower = incident_text.lower()
        
        # Anahtar kelime taraması
        keywords_found = {}
        for category, keywords in self.KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in text_lower)
            keywords_found[category] = count > 0
        
        # Detay göstergeleri
        indicators = {
            "has_timeline": any(k in text_lower for k in ["kronoloji", "timeline", "saat:"]),
            "has_witness": any(k in text_lower for k in ["tanık", "witness", "beyan"]),
            "has_procedure": any(k in text_lower for k in ["prosedür", "loto", "iş izni"]),
            "has_root_cause": any(k in text_lower for k in ["kök neden", "root cause", "neden:"]),
            "has_management": any(k in text_lower for k in ["yönetim", "management", "baskı"]),
            "word_count": len(incident_text.split()),
        }
        
        # Seviye belirleme
        detail_score = sum([
            indicators["has_timeline"] * 2,
            indicators["has_witness"] * 2,
            indicators["has_procedure"] * 2,
            indicators["has_root_cause"] * 3,
            indicators["has_management"] * 2,
            (indicators["word_count"] > 500) * 2,
        ])
        
        if detail_score >= 8:
            level = 1  # Detaylı (test formatı gibi)
        elif detail_score >= 4:
            level = 2  # Orta
        else:
            level = 3  # Minimal
        
        # Mevcut ve eksik bilgileri listele
        present = [k for k, v in keywords_found.items() if v]
        missing = [k for k, v in keywords_found.items() if not v]
        
        return level, {
            "present": present,
            "missing": missing,
            "keywords_found": keywords_found,
            "indicators": indicators,
            "detail_score": detail_score,
        }
    
    def generate_missing_questions(self, missing_categories: List[str], 
                                   incident_type: str = "generic") -> List[Dict]:
        """
        Eksik kategoriler için sorular üretir.
        
        Args:
            missing_categories: Eksik bilgi kategorileri
            incident_type: Olay tipi (elektrik, düşme, forklift, vb.)
        
        Returns:
            [{"category": "prosedür", "question": "...", "options": [...]}]
        """
        questions = []
        
        # Olay tipine göre özelleştirilmiş sorular
        question_templates = {
            "elektrik": {
                "prosedür": "LOTO (Lockout/Tagout) prosedürü uygulandı mı?",
                "ppe": "Elektrikçi eldiveni ve yalıtımlı ayakkabı kullanıldı mı?",
                "ekipman": "Elektrik paneli son bakımı ne zaman yapıldı?",
            },
            "düşme": {
                "prosedür": "Yüksekte çalışma izni alındı mı?",
                "ppe": "Emniyet kemeri takılı mıydı?",
                "ekipman": "Korkuluk/güvenlik ağı var mıydı?",
            },
            "forklift": {
                "prosedür": "Forklift kullanım izni ve yetkilendirme var mıydı?",
                "ppe": "Sürücü emniyet kemeri takıyor muydu?",
                "ekipman": "Forklift ikaz sistemi (geri vites) çalışıyor muydu?",
            },
            "generic": {
                "prosedür": "İş için özel bir prosedür var mıydı?",
                "ppe": "Gerekli kişisel koruyucu ekipman kullanıldı mı?",
                "ekipman": "Ekipman düzenli bakıma tabi miydi?",
                "eğitim": "İlgili personel bu iş için eğitim almış mıydı?",
                "yönetim": "Yönetim bu konuda daha önce uyarı/denetim yaptı mı?",
            }
        }
        
        # Olay tipine göre şablon seç
        templates = question_templates.get(incident_type, question_templates["generic"])
        
        for category in missing_categories:
            if category in templates:
                questions.append({
                    "category": category,
                    "question": templates[category],
                    "options": self._get_default_options(category),
                })
        
        return questions
    
    def _get_default_options(self, category: str) -> List[Dict]:
        """Kategoriye göre varsayılan cevap seçenekleri"""
        
        if category == "prosedür":
            return [
                {
                    "label": "Hayır, prosedür hiç yoktu",
                    "code": "D4.1",
                    "follow_up": "why_no_procedure"
                },
                {
                    "label": "Evet, prosedür vardı ama uygulanmıyordu",
                    "code": "D4.2",
                    "follow_up": "why_not_applied"
                },
                {
                    "label": "Prosedür genelde uygulanır, bu sefer atlandı",
                    "code": "A1.1",
                    "follow_up": "why_skipped_once"
                }
            ]
        
        elif category == "eğitim":
            return [
                {
                    "label": "Hayır, eğitim verilmemişti",
                    "code": "D3.1",
                    "follow_up": None
                },
                {
                    "label": "Eğitim verilmişti ama yeterli değildi",
                    "code": "D3.1",
                    "follow_up": "training_quality"
                },
                {
                    "label": "Eğitim verilmişti ve yeterliydi",
                    "code": None,
                    "follow_up": "other_factors"
                }
            ]
        
        elif category == "yönetim":
            return [
                {
                    "label": "Yönetim bu sapmaları biliyordu ama tolerans gösterdi",
                    "code": "D1.9",
                    "follow_up": None
                },
                {
                    "label": "Üretim baskısı güvenliği bastırdı",
                    "code": "D1.4",
                    "follow_up": None
                },
                {
                    "label": "Denetim/gözetim yetersizdi",
                    "code": "D1.2",
                    "follow_up": None
                }
            ]
        
        else:
            return [
                {"label": "Evet", "code": None, "follow_up": None},
                {"label": "Hayır", "code": None, "follow_up": None},
                {"label": "Kısmen", "code": None, "follow_up": None},
            ]
```

---

### **3. `question_engine.py` - Akıllı Soru Üretimi**

```python
"""
Intelligent Question Engine - Bağlamsal Soru Üretimi
"""

from typing import Dict, List, Optional
from agents.knowledge_base import HSG245_TAXONOMY


class QuestionEngine:
    """
    Knowledge base'den bağlamsal sorular üretir.
    Olay tipine göre özelleştirir ve dallanma mantığı kurar.
    """
    
    def __init__(self, knowledge_base: dict = None):
        self.kb = knowledge_base or HSG245_TAXONOMY
        self.question_history = []  # Soru geçmişi
        
    def generate_contextual_question(
        self, 
        context: Dict, 
        current_code: Optional[str] = None,
        incident_type: str = "generic"
    ) -> Dict:
        """
        Bağlamsal soru üretir.
        
        Args:
            context: Mevcut olay bilgisi
            current_code: Şu anki HSG kod (varsa)
            incident_type: Olay tipi
        
        Returns:
            {
                "question_id": "q_001",
                "question_text": "...",
                "question_type": "multiple_choice" | "open_ended",
                "options": [...],
                "context_hint": "...",  # Kullanıcıya ipucu
            }
        """
        
        # Eğer bir kod belirtilmişse, onun için follow-up sor
        if current_code:
            return self._generate_follow_up(current_code, context)
        
        # İlk aşama: Doğrudan neden (A/B kategorileri)
        if not self.question_history:
            return self._generate_initial_cause_question(context, incident_type)
        
        # Orta aşama: Sisteme giriş (C/D kategorileri)
        return self._generate_system_question(context)
    
    def _generate_initial_cause_question(self, context: Dict, incident_type: str) -> Dict:
        """İlk görünür neden sorusu (A/B)"""
        
        if incident_type == "elektrik":
            return {
                "question_id": "q_initial_elektrik",
                "question_text": "Bu elektrik olayında fiziksel bir koşul mu, yoksa davranışsal bir durum mu vardı?",
                "question_type": "multiple_choice",
                "options": [
                    {
                        "label": "B1.5: Uyarı/alarm sistemleri arızalı (ör: voltmetre arızası)",
                        "code": "B1.5",
                        "category": "condition",
                        "follow_up": "equipment_check"
                    },
                    {
                        "label": "A3.2: Gerekli KKD kullanılmadı (eldiven, ayakkabı)",
                        "code": "A3.2",
                        "category": "action",
                        "follow_up": "ppe_availability"
                    },
                    {
                        "label": "B4.5: Enerji izolasyonu yapılmadı (LOTO uygulanmadı)",
                        "code": "B4.5",
                        "category": "condition",
                        "follow_up": "loto_procedure"
                    }
                ],
                "context_hint": "Elektrik olaylarında genelde enerji izolasyonu (LOTO) veya KKD eksikliği görülür."
            }
        
        elif incident_type == "düşme":
            return {
                "question_id": "q_initial_fall",
                "question_text": "Düşme olayının temel nedeni neydi?",
                "question_type": "multiple_choice",
                "options": [
                    {
                        "label": "B4.4: Korunmasız yükseklik (korkuluk yoktu)",
                        "code": "B4.4",
                        "category": "condition",
                        "follow_up": "guardrail_check"
                    },
                    {
                        "label": "A3.2: Emniyet kemeri kullanılmadı",
                        "code": "A3.2",
                        "category": "action",
                        "follow_up": "harness_availability"
                    },
                    {
                        "label": "B1.1: Kaygan/düzensiz zemin",
                        "code": "B1.1",
                        "category": "condition",
                        "follow_up": "surface_condition"
                    }
                ],
                "context_hint": "Düşme olaylarında korkuluk eksikliği veya emniyet kemeri kullanılmaması yaygındır."
            }
        
        else:  # generic
            return {
                "question_id": "q_initial_generic",
                "question_text": "Olayın doğrudan nedeni neydi?",
                "question_type": "multiple_choice",
                "options": [
                    {
                        "label": "A kategorisi: İnsan davranışı (kural ihlali, dikkat dağınıklığı)",
                        "code": "A",
                        "category": "action",
                        "follow_up": "action_detail"
                    },
                    {
                        "label": "B kategorisi: Fiziksel koşul (ekipman arızası, tehlikeli ortam)",
                        "code": "B",
                        "category": "condition",
                        "follow_up": "condition_detail"
                    }
                ],
                "context_hint": "İlk olarak olayın davranışsal mı yoksa koşulsal mı olduğunu belirleyelim."
            }
    
    def _generate_follow_up(self, code: str, context: Dict) -> Dict:
        """
        Belirli bir kod için takip sorusu üretir.
        
        Örnek: B4.5 (LOTO uygulanmadı) → "LOTO prosedürü var mıydı?"
        """
        
        # LOTO ile ilgili kodlar
        if code == "B4.5":  # Enerji izolasyonu yapılmadı
            return {
                "question_id": f"q_follow_{code}",
                "question_text": "LOTO (Lockout/Tagout) prosedürü şirkette mevcut muydu?",
                "question_type": "multiple_choice",
                "options": [
                    {
                        "label": "Hayır, LOTO prosedürü hiç yoktu",
                        "code": "D4.1",  # Prosedür yok
                        "follow_up": "why_no_procedure"
                    },
                    {
                        "label": "Evet, prosedür vardı ama uygulanmıyordu",
                        "code": "D4.2",  # Prosedür etkisiz
                        "follow_up": "why_not_applied"
                    },
                    {
                        "label": "Prosedür vardı, genelde uygulanır, bu sefer atlandı",
                        "code": "A1.1",  # Bireysel ihlal
                        "follow_up": "why_skipped_once"
                    }
                ],
                "context_hint": "LOTO prosedürünün varlığı ile uygulanması farklı şeylerdir."
            }
        
        # KKD ile ilgili kodlar
        elif code == "A3.2":  # KKD kullanılmadı
            return {
                "question_id": f"q_follow_{code}",
                "question_text": "Gerekli kişisel koruyucu ekipman (KKD) mevcut muydu?",
                "question_type": "multiple_choice",
                "options": [
                    {
                        "label": "Hayır, KKD hiç verilmemişti",
                        "code": "D6.1",  # Ekipman sağlanmamış
                        "follow_up": "why_no_ppe"
                    },
                    {
                        "label": "Evet, KKD vardı ama kullanılmadı",
                        "code": "A3.2",  # Bireysel tercih
                        "follow_up": "why_not_worn"
                    },
                    {
                        "label": "KKD vardı ama uygun değildi (yanlış tip)",
                        "code": "D6.1",  # Yanlış ekipman
                        "follow_up": "equipment_selection"
                    }
                ],
                "context_hint": "KKD'nin olup olmaması ile kullanılıp kullanılmaması farklı kök nedenlere işaret eder."
            }
        
        # Prosedür var ama uygulanmıyor
        elif code == "D4.2":
            return {
                "question_id": f"q_follow_{code}",
                "question_text": "Prosedür neden uygulanmıyordu?",
                "question_type": "multiple_choice",
                "options": [
                    {
                        "label": "Eğitim verilmemişti, personel prosedürü bilmiyordu",
                        "code": "D3.1",
                        "follow_up": None  # Kök neden bulundu
                    },
                    {
                        "label": "Zaman baskısı/üretim hedefi nedeniyle atlanıyordu",
                        "code": "D1.4",
                        "follow_up": None  # Kök neden bulundu
                    },
                    {
                        "label": "Yönetim bu sapmaları biliyor ama tolerans gösteriyordu",
                        "code": "D1.9",
                        "follow_up": None  # Kök neden bulundu
                    },
                    {
                        "label": "Denetim yoktu, kimse kontrol etmiyordu",
                        "code": "D1.2",
                        "follow_up": None  # Kök neden bulundu
                    }
                ],
                "context_hint": "Prosedürün uygulanmamasının arkasında genelde eğitim, baskı veya gözetim eksikliği vardır."
            }
        
        # Varsayılan genel soru
        else:
            return {
                "question_id": f"q_follow_{code}_generic",
                "question_text": f"Kod {code} tespit edildi. Bunun arkasındaki organizasyonel neden nedir?",
                "question_type": "multiple_choice",
                "options": [
                    {"label": "Eğitim eksikliği", "code": "D3.1", "follow_up": None},
                    {"label": "Prosedür/sistem eksikliği", "code": "D4.1", "follow_up": None},
                    {"label": "Gözetim/denetim eksikliği", "code": "D1.2", "follow_up": None},
                    {"label": "Üretim baskısı", "code": "D1.4", "follow_up": None},
                ],
                "context_hint": "Organizasyonel faktörleri araştırıyoruz (D kategorisi)."
            }
    
    def _generate_system_question(self, context: Dict) -> Dict:
        """Sisteme giriş sorusu (neden prosedür/eğitim/denetim eksik?)"""
        pass  # Daha sonra genişletilebilir
```

---

### **4. `gradio_app.py` - Ana Arayüz**

```python
"""
Gradio HITL Application - Hibrit Giriş Destekli
"""

import gradio as gr
from hybrid_input_processor import HybridInputProcessor
from question_engine import QuestionEngine
from agents.rootcause_agent_v2 import RootCauseAgentV2


# Global state
state = {
    "incident_text": "",
    "input_level": None,
    "missing_info": [],
    "current_question_index": 0,
    "answers": {},
    "branches": [],
}


# Processors
input_processor = HybridInputProcessor()
question_engine = QuestionEngine()
rca_agent = RootCauseAgentV2()


def analyze_incident_input(incident_text: str):
    """
    TAB 1: Olay girişini analiz eder.
    """
    level, details = input_processor.detect_input_level(incident_text)
    
    state["incident_text"] = incident_text
    state["input_level"] = level
    state["missing_info"] = details["missing"]
    
    if level == 1:
        # Detaylı rapor: Direkt analize geç
        return f"""
        ## ✅ Yeterli Detay Mevcut!
        
        **Girdi Seviyesi:** Level {level} (Detaylı)
        
        **Tespit Edilen Bilgiler:**
        {", ".join(details["present"])}
        
        Direkt kök neden analizine geçebiliriz.
        
        [Analize Başla] butonuna basın.
        """
    
    elif level == 2:
        # Orta detay: Eksiklikleri sor
        missing_str = ", ".join(details["missing"])
        return f"""
        ## 🔍 Eksik Bilgi Tespiti
        
        **Girdi Seviyesi:** Level {level} (Orta)
        
        **Mevcut Bilgiler:** {", ".join(details["present"])}
        
        **Eksik Bilgiler:** {missing_str}
        
        Bu bilgileri tamamlamak için {len(details["missing"])} soru soracağım.
        
        [TAB 2: Sorgulama]'ya geçin.
        """
    
    else:
        # Minimal: Çok soru sor
        return f"""
        ## ❓ Detaylı Sorgulama Gerekli
        
        **Girdi Seviyesi:** Level {level} (Minimal)
        
        Kapsamlı analiz için 8-10 soru soracağım.
        
        [TAB 2: Sorgulama]'ya geçin veya daha fazla bilgi ekleyin.
        """


def get_next_question():
    """
    TAB 2: Bir sonraki soruyu gösterir.
    """
    if state["current_question_index"] >= len(state["missing_info"]):
        return "✅ Tüm sorular tamamlandı! TAB 3'e geçin."
    
    # İlk soruyu üret
    category = state["missing_info"][state["current_question_index"]]
    question = question_engine.generate_contextual_question(
        context={"description": state["incident_text"]},
        incident_type="elektrik"  # Otomatik tespit edilebilir
    )
    
    # Gradio HTML formatında soru
    html = f"""
    <h3>❓ Soru {state["current_question_index"] + 1}/{len(state["missing_info"])}</h3>
    <p><strong>{question["question_text"]}</strong></p>
    """
    
    return html, question["options"]


def submit_answer(selected_option):
    """
    TAB 2: Kullanıcı cevabını kaydeder.
    """
    state["answers"][state["current_question_index"]] = selected_option
    state["current_question_index"] += 1
    
    if state["current_question_index"] < len(state["missing_info"]):
        return get_next_question()
    else:
        return "✅ Tüm sorular tamamlandı! TAB 3'e geçin.", []


# Gradio Arayüzü
with gr.Blocks(title="HSE Kök Neden Analizi - HITL") as app:
    gr.Markdown("# 🔍 HSE Kök Neden Analizi - Human-in-the-Loop")
    
    with gr.Tab("1️⃣ Olay Girişi"):
        gr.Markdown("## Olayı Açıklayın")
        gr.Markdown("**3 farklı detay seviyesinde girebilirsiniz:**")
        gr.Markdown("- **Detaylı:** Test formatı (kronoloji, tanık, prosedür ihlali)")
        gr.Markdown("- **Orta:** Yapılandırılmış form (olay özeti + temel ihlaller)")
        gr.Markdown("- **Minimal:** Serbest metin (1-2 paragraf)")
        
        incident_input = gr.Textbox(
            label="Olay Açıklaması",
            placeholder="Örn: Forklift geri manevra yaparken çalışana çarptı...",
            lines=10
        )
        analyze_btn = gr.Button("Analiz Et", variant="primary")
        analysis_output = gr.Markdown()
        
        analyze_btn.click(analyze_incident_input, incident_input, analysis_output)
    
    with gr.Tab("2️⃣ Sorgulama"):
        gr.Markdown("## AI Soruları")
        question_display = gr.HTML()
        answer_radio = gr.Radio(label="Seçiminiz", choices=[])
        submit_answer_btn = gr.Button("İlerle")
        answer_feedback = gr.Markdown()
        
        # İlk soruyu göster
        app.load(get_next_question, outputs=[question_display, answer_radio])
        
        submit_answer_btn.click(
            submit_answer,
            answer_radio,
            [answer_feedback, answer_radio]
        )
    
    with gr.Tab("3️⃣ Kod Onayı"):
        gr.Markdown("## Kök Neden Kodları")
        gr.Markdown("AI'nın önerdiği kodları gözden geçirin ve onaylayın.")
        
        # Burada kod önerileri gösterilir
        code_suggestions = gr.DataFrame(
            headers=["Dal", "Kod", "Açıklama", "Onayla"],
            label="Kök Neden Önerileri"
        )
        approve_all_btn = gr.Button("Tümünü Onayla", variant="primary")
    
    with gr.Tab("4️⃣ Rapor"):
        gr.Markdown("## Nihai Rapor")
        report_preview = gr.HTML()
        download_docx = gr.File(label="DOCX İndir")
        download_html = gr.File(label="HTML İndir")


if __name__ == "__main__":
    app.launch()
```

---

## 📊 Veri Akışı Diyagramı

```
┌───────────────────────────────────────────────────────────┐
│ KULLANICI GİRİŞİ                                          │
│ (3 seviye: Detaylı / Orta / Minimal)                      │
└───────────────────────────────────────────────────────────┘
                        ▼
┌───────────────────────────────────────────────────────────┐
│ HYBRID INPUT PROCESSOR                                    │
│ - Girdi seviyesini tespit et                              │
│ - Anahtar kelime taraması                                 │
│ - Eksik bilgileri listele                                 │
└───────────────────────────────────────────────────────────┘
                        ▼
            ┌───────────┴───────────┐
            ▼                       ▼
┌──────────────────┐    ┌──────────────────────────┐
│ SEVİYE 1: DETAY  │    │ SEVİYE 2/3: EKSIK BİLGİ  │
│ Direkt analiz    │    │ Sorgulama gerekli        │
└──────────────────┘    └──────────────────────────┘
            │                       │
            │                       ▼
            │           ┌──────────────────────────┐
            │           │ QUESTION ENGINE          │
            │           │ - Bağlamsal soru üret    │
            │           │ - Dallanma mantığı       │
            │           └──────────────────────────┘
            │                       │
            │                       ▼
            │           ┌──────────────────────────┐
            │           │ KULLANICI CEVAPLAR       │
            │           │ (Gradio arayüzü)         │
            │           └──────────────────────────┘
            │                       │
            └───────────┬───────────┘
                        ▼
┌───────────────────────────────────────────────────────────┐
│ COMPLETE DATA (Tamamlanmış Veri)                          │
│ - Olay özeti + Kronoloji + Prosedür + Tanık + Yönetim    │
└───────────────────────────────────────────────────────────┘
                        ▼
┌───────────────────────────────────────────────────────────┐
│ ROOT CAUSE AGENT V2                                       │
│ - 5-Why analizi                                           │
│ - HSG245 kod önerileri                                    │
└───────────────────────────────────────────────────────────┘
                        ▼
┌───────────────────────────────────────────────────────────┐
│ APPROVAL LOOP                                             │
│ - Kullanıcı kodları onayla/düzelt/reddet                  │
└───────────────────────────────────────────────────────────┘
                        ▼
┌───────────────────────────────────────────────────────────┐
│ SKILLBASED DOCX AGENT                                     │
│ - Rapor üretimi (DOCX + HTML)                            │
└───────────────────────────────────────────────────────────┘
```

---

## 🧪 Test Senaryoları

### **Test 1: Detaylı Giriş (test_hitl_detailed.py)**

```python
"""
Test: Detaylı rapor girişi (test formatı)
Beklenen: Direkt kök neden analizi, sorgulama YOK
"""

def test_detailed_input():
    incident_text = """
    OLAY RAPORU - ELEKTRİK ÇARPMASI
    ...
    [Tam test formatı buraya]
    """
    
    processor = HybridInputProcessor()
    level, details = processor.detect_input_level(incident_text)
    
    assert level == 1, f"Detaylı girdi Level 1 olmalı, {level} çıktı"
    assert len(details["missing"]) < 2, "Eksik bilgi çok fazla"
    
    # Direkt RCA'ya geç
    rca_agent = RootCauseAgentV2()
    result = rca_agent.analyze_root_causes(...)
    
    assert len(result["final_root_causes"]) >= 2
    print("✅ Detaylı giriş testi başarılı")
```

### **Test 2: Minimal Giriş (test_hitl_minimal.py)**

```python
"""
Test: Minimal giriş (serbest metin)
Beklenen: 8-10 soru, adım adım tamamlama
"""

def test_minimal_input():
    incident_text = "Forklift geri manevra yaparken çalışana çarptı."
    
    processor = HybridInputProcessor()
    level, details = processor.detect_input_level(incident_text)
    
    assert level == 3, f"Minimal girdi Level 3 olmalı, {level} çıktı"
    assert len(details["missing"]) >= 5, "Eksik bilgi tespit edilmeli"
    
    # Soru üretimi
    engine = QuestionEngine()
    questions = engine.generate_missing_questions(details["missing"], "forklift")
    
    assert len(questions) >= 5, "En az 5 soru üretilmeli"
    print(f"✅ {len(questions)} soru üretildi")
```

### **Test 3: Hibrit Akış (test_hitl_hybrid.py)**

```python
"""
Test: Orta detaylı giriş + sorgulama + onay döngüsü
Beklenen: Hibrit akış, kullanıcı müdahalesi ile tamamlanma
"""

def test_hybrid_workflow():
    # Orta detaylı giriş
    incident_text = """
    Teknisyen elektrik panosunda çalışırken 380V akımına kapıldı.
    LOTO prosedürü uygulanmadı.
    Teknisyen hastaneye kaldırıldı.
    """
    
    # Adım 1: Eksiklik tespiti
    processor = HybridInputProcessor()
    level, details = processor.detect_input_level(incident_text)
    assert level == 2, "Orta seviye olmalı"
    
    # Adım 2: Sorgulama
    engine = QuestionEngine()
    question_1 = engine.generate_contextual_question(
        context={"description": incident_text},
        incident_type="elektrik"
    )
    
    # Kullanıcı cevabı simülasyonu
    user_answer_1 = {
        "question_id": question_1["question_id"],
        "selected_option": "Evet, prosedür vardı ama uygulanmıyordu",
        "code": "D4.2"
    }
    
    # Takip sorusu
    question_2 = engine._generate_follow_up("D4.2", {})
    assert "neden uygulanmıyordu" in question_2["question_text"].lower()
    
    # Kullanıcı cevabı 2
    user_answer_2 = {
        "question_id": question_2["question_id"],
        "selected_option": "Üretim baskısı",
        "code": "D1.4"
    }
    
    # Kök neden bulundu!
    print("✅ Hibrit akış testi başarılı - Kök neden: D1.4")
```

---

## 🎯 Özet

Bu tasarım belgesi, **hibrit HITL sistemi**nin tam detayını içermektedir:

### **Temel Özellikler:**
1. ✅ **3 seviye esneklik**: Detaylı/Orta/Minimal giriş
2. ✅ **Akıllı eksiklik tespiti**: Anahtar kelime + bağlam analizi
3. ✅ **Bağlamsal sorgulama**: Olay tipine göre özelleşmiş sorular
4. ✅ **Dallanma mantığı**: if-then sorgu ağacı
5. ✅ **Test formatı desteği**: Mevcut test dosyaları direkt kullanılabilir
6. ✅ **Gradio arayüzü**: Adım adım wizard
7. ✅ **Onay döngüsü**: Kod önerilerini düzelt/onayla/reddet

### **Sonraki Adımlar:**
1. `hybrid_input_processor.py` kodunu yaz
2. `question_engine.py` kodunu yaz
3. `gradio_app.py` ile arayüz oluştur
4. Test senaryolarını çalıştır
5. Gerçek kullanıcı testleri

---

**DURUM:** Tasarım tamamlandı, kodlama başlayabilir ✅

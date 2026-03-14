# HSE RCA — HITL + Agentic AI Entegrasyon Planı V2

**Tarih:** 3 Mart 2026  
**Versiyon:** 2.0 — Mimari Düzeltmesi  
**Değişiklik:** V1'deki yanlış varsayım düzeltildi: Kullanıcı Immediate Cause seçmiyor.

---

## Kritik Mimari Fark (V1 → V2)

| | V1 (YANLIŞ) | V2 (DOĞRU) |
|---|---|---|
| Immediate Cause | Kullanıcı menüden seçiyor | **Agent otomatik buluyor** |
| Kullanıcının rolü | Kod seçmek | Sadece soruları cevaplamak |
| Sorular nereden geliyor | FIVE_WHY_TREE (sabit ağaç) | **Agent'ın bulduğu kodlara göre dinamik** |
| Kök neden kararı | Keyword matching | **Agent, kullanıcı cevaplarına göre karar veriyor** |

---

## 1. Gerçek Problem

`RootCauseAgentV2` şu anda:
- Olay metnini → Immediate Cause (A/B) → 5-Why → Root Cause (C/D) olarak analiz ediyor ✅
- Ama tüm bu analizi **tek seferde, kullanıcısız** yapıyor ❌
- Aynı olay metni → her seferinde benzer Immediate Cause → benzer Root Cause ❌
- D4.1 "Risk değerlendirmesi eksik" gibi **jenerik kodlara** sıklıkla gidiyor ❌

**Neden jenerik gidiyor?**  
Çünkü agent sadece olay metnini görüyor. Metinde "risk değerlendirmesi yapıldı mı?" diye bir bilgi yoksa, agent varsayılan olarak D4.1'e gidiyor.

Oysa:
- Risk değerlendirmesi **yapıldı ama tehlike belirlendi → önlem uygulanmadı** → **D4.2**
- Risk değerlendirmesi **değişim sonrası güncellenmedi** → **D4.3**
- **İş izni sistemi** etkisizdi → **D4.4**
- **LOTO** eksikti → **D4.5**

Bu ayrımı ancak soruşturmacı sorup öğrenebilir. İşte HITL'ın amacı bu.

---

## 2. Hedef: Ne Yapacak Bu Sistem?

```
KULLANICI: "Hasan Yıldız iskelede düştü, 6 metre yükseklikten"
                │
                ▼
    ┌─────────────────────────────┐
    │  AŞAMA 1: Olay Analizi      │  (otomatik, arka planda)
    │  OverviewAgent → part1      │
    │  AssessmentAgent → part2    │
    │  RootCauseAgent →           │
    │    Immediate Causes tespit  │  ← Agent buluyor: B4.4, A3.2
    └──────────────┬──────────────┘
                   │
                   ▼
    ┌─────────────────────────────────────────────────────┐
    │  AŞAMA 2: HITL Derinleştirme Soruları               │
    │                                                     │
    │  Bot: "B4.4 (Korunmasız yükseklik) tespit edildi.  │
    │        Şimdi kök nedenini bulmak için sorular       │
    │        soracağım:"                                  │
    │                                                     │
    │  Bot: "Bariyer veya korkuluk var mıydı?             │
    │        → Hiç yoktu / Vardı ama yetersizdi /        │
    │          Vardı ama aşıldı"                          │
    │                                                     │
    │  Kullanıcı: "Vardı ama tamamlanmamıştı, montaj     │
    │              yarım kalmıştı"                        │
    │                                                     │
    │  Bot: "İş izni (PTW) alındı mıydı bu çalışma için?│
    │        İzin belgesi koşulları kontrol edildi mi?"   │
    │                                                     │
    │  Kullanıcı: "İzin belgesi imzalandı ama sahada     │
    │              hiç kontrol edilmedi"                  │
    │                                                     │
    │  Bot: "Risk değerlendirmesinde bu tehlike           │
    │        belirlenmişti. Peki belirlenen kontroller    │
    │        sahaya yansıtılmış mıydı?"                   │
    │                                                     │
    │  Kullanıcı: "Risk değerlendirmesinde bariyer        │
    │              montajı tamamlanmadan çalışılmayacak  │
    │              yazıyordu ama kimse kontrol etmedi"    │
    └──────────────┬──────────────────────────────────────┘
                   │
                   ▼
    ┌─────────────────────────────────────────────────────┐
    │  AŞAMA 3: Agent Final Analiz                        │
    │                                                     │
    │  RootCauseAgentV2 çalışıyor:                        │
    │  • Olay metni +                                     │
    │  • Kullanıcı cevapları (bariyer vardı, PTW vardı    │
    │    ama kontrol edilmedi, risk analizi vardı ama     │
    │    sahaya yansımadı)                                │
    │                                                     │
    │  Sonuç:                                             │
    │  ❌ D4.1 (Risk analizi yok) → YANLIŞ, analiz VARDI │
    │  ✅ D4.2 (Kontroller uygulanmadı) → DOĞRU          │
    │  ✅ D4.4 (İş izni etkisiz) → DOĞRU                 │
    └─────────────────────────────────────────────────────┘
```

---

## 3. Sorular Nasıl Üretilecek?

Sabit soru ağacı (FIVE_WHY_TREE) **kaldırılmıyor** — ama birincil soru kaynağı olmaktan çıkıyor.

### Yeni soru üretim mantığı:

```
Agent tespit etti: [B4.4, A3.2]
        │
        ▼
HSG245_DISAMBIGUATION_QUESTIONS["B4.4"] → soruları getir
        │
        ▼
Soru 1: "Düşme koruması (bariyer/korkuluk) mevcut muydu?"
  → "Hiç yoktu" → D4.1 veya D5.1 yönünde ilerle
  → "Vardı ama yetersizdi" → D4.2 veya D5.1 yönünde ilerle  
  → "Vardı ama ihlal edildi" → A1.1 yönünde ilerle

Soru 2: "İş izni/PTW sistemi işledi mi?"
  → "Yok" → D4.1 yönünde ilerle
  → "Var ama kontrol edilmedi" → D4.4 yönünde ilerle

Soru 3: "Çalışanlara yüksekte çalışma eğitimi verildi mi?"
  → "Hiç verilmedi" → D3.1 yönünde ilerle
  → "Verildi ama eski/tazelenmedi" → D3.6 yönünde ilerle

... (5 soruya kadar)
        │
        ▼
RootCauseAgentV2: Bu spesifik cevaplarla → D4.2 + D4.4 → final karar
```

---

## 4. HSG245 Disambiguation Soruları

Her Immediate Cause kodu için **HSG245 taxonomy'deki "Seçme" notlarından türetilmiş** sorular.

Bu sorular agentle olayı D4.1'den D4.2'ye, D4.5'e, D3.1'e yönlendirmek için tasarlandı.

### Örnek: B4.4 (Korunmasız yükseklik)

```python
"B4.4": [
    {
        "soru": "Çalışma yapılan yerde bariyer, korkuluk veya güvenlik ağı var mıydı?",
        "amaç": "D4.1 vs D4.2 vs D5.1 ayrımı",
        "yönler": {
            "hiç yoktu|kurulmamış|yoktu": "D4.1 veya D5.1 — tehlike belirlenmemiş",
            "vardı ama|yetersiz|eksikti": "D4.2 — kontrol belirlendi ama uygulanmadı",
            "aşıldı|geçildi|ihlal": "A1.1 — bilerek ihlal",
        }
    },
    {
        "soru": "Bu çalışma için iş izni (PTW) alındı mıydı? İzin koşulları sahada kontrol edildi mi?",
        "amaç": "D4.4 ayrımı",
        "yönler": {
            "izin yok|alınmadı|yoktu": "D4.1 — iş izni sistemi yok",
            "alındı ama|imzalandı ama|kontrol edilmedi": "D4.4 — iş izni etkisiz",
        }
    },
    {
        "soru": "Bu çalışma için risk değerlendirmesi yapılmış mıydı? Tehlike belirlenmişti ama önlem uygulanmadı mıydı?",
        "amaç": "D4.1 vs D4.2 ayrımı — KRİTİK SORU",
        "yönler": {
            "yapılmamış|hiç yoktu|belirlenmemiş": "D4.1 — analiz gerçekten yok",
            "yapıldı ama|belirlendi ama|uygulanmadı": "D4.2 — analiz var, önlem yok",
            "değişim|güncellenmedi|eskimiş": "D4.3 — değişim yönetimi eksik",
        }
    },
    {
        "soru": "Yönetim bariyer eksikliğinden haberdardı mıydı? Bilerek devam edildi mi?",
        "amaç": "D1.4 / D1.9 ayrımı",
        "yönler": {
            "biliyordu|haberdar|göz yumdu": "D1.9 — yönetim toleransı",
            "üretim|baskı|yetiştir": "D1.4 — üretim baskısı",
        }
    },
    {
        "soru": "Yüksekte çalışma eğitimi verilmiş miydi? Ne zaman?",
        "amaç": "D3.1 vs D3.6 ayrımı",
        "yönler": {
            "hiç verilmedi|yoktu|almamış": "D3.1 — eğitim hiç yok",
            "eski|tazelenmedi|yıl önce|ay önce": "D3.6 — eğitim etkinliği ölçülmüyor",
        }
    },
]
```

### Örnek: B3.2 (Elektrik enerjisi)

```python
"B3.2": [
    {
        "soru": "LOTO (Kilitleme/Etiketleme) prosedürü uygulandı mıydı? Ekipman enerji izole edildi mi?",
        "amaç": "D4.5 vs A1.1 ayrımı",
        "yönler": {
            "uygulanmadı|yoktu|prosedür yok|hiç": "D4.5 — LOTO sistemi yok/eksik",
            "uygulandı ama|kısmen|tam olmadı": "D4.5 — LOTO etkisiz",
            "biliyordu ama|kasıtlı|atladı": "A1.1 — bilinçli ihlal",
        }
    },
    {
        "soru": "Çalışma öncesinde iş izni (PTW) alındı mıydı?",
        "amaç": "D4.4 ayrımı",
        "yönler": {
            "alınmadı|yoktu": "D4.1 veya D4.4",
            "alındı ama|kontrol edilmedi": "D4.4 — iş izni etkisiz",
        }
    },
    {
        "soru": "Elektrik çalışması için yetki belgesi/sertifikası olan kişi görevlendirildi mi?",
        "amaç": "D3.1 / D3.4 ayrımı",
        "yönler": {
            "yetki yok|belge yok|sertifika yok": "D3.1 veya D3.4",
            "vardı ama": "D3.3 — pratik eğitim eksik",
        }
    },
    {
        "soru": "Yönetim bu riski biliyor muydu? Enerji izolasyonu yapılmadan çalışma 'norm' hale gelmiş miydi?",
        "amaç": "D1.5 / D1.9 ayrımı",
        "yönler": {
            "hep böyle|norm|alışkanlık": "D1.5 — sapmanın normalleşmesi",
            "yönetim biliyordu|göz yumdu": "D1.9 — yönetim toleransı",
        }
    },
    {
        "soru": "Bu ekipman/sistem için son risk değerlendirmesi ne zaman yapılmıştı?",
        "amaç": "D4.1 vs D4.3 ayrımı",
        "yönler": {
            "yapılmamış|hiç": "D4.1 — analiz yok",
            "eski|güncellenmedi|değişim oldu": "D4.3 — değişim yönetimi eksik",
        }
    },
]
```

---

## 5. Yeni Akış (Chatbot Adım Adım)

```
Adım 1: "Olayı anlatın"
         └─ Kullanıcı olay metnini yazar
         └─ OverviewAgent + AssessmentAgent arka planda çalışır (part1, part2)
         └─ RootCauseAgent SADECE Immediate Causes belirler (5-Why yapmaz henüz)
         └─ Tespit: ["B4.4", "A3.2"] gibi

Adım 2: Bot derinleştirme sorularını sorar
         └─ B4.4 için → HSG245_DISAMBIGUATION["B4.4"] sorularını sıralar
         └─ A3.2 varsa → ona da sorular sorar
         └─ Toplam ~5-8 soru (tüm tespit edilen kodlar için)

Adım 3: Kullanıcı cevapları verir (her soruya metin)

Adım 4: "Analiz ediliyor..." mesajı
         └─ RootCauseAgentV2.analyze_root_causes() çağrılır
         └─ investigation_data içinde:
            - olay metni
            - part1, part2
            - kullanıcının cevapları (why_answers)
         └─ Agent artık jenerik D4.1'e değil, cevaplara göre D4.2/D4.4/D1.9'a gidiyor

Adım 5: Chatbotta sonuç gösterilir
         └─ 5-Why zinciri (agent yazısıyla, detaylı)
         └─ Final kök nedenler (D4.2, D4.4 gibi — spesifik)
         └─ SkillBasedDocxAgent → HTML/DOCX rapor

```

---

## 6. Dosya Değişiklikleri (Güncellenmiş)

| Dosya | Durum | Ne Değişiyor |
|-------|-------|--------------|
| `hitl_test/hitl_disambiguation.py` | **YENİ DOSYA** | Her Immediate Cause kodu için HSG245 disambiguation soruları |
| `agents/rootcause_agent_v2.py` | **Güncelleniyor** | `_append_hitl_answers()` + `analyze_root_causes()` HITL cevaplarını görüyor |
| `hitl_test/five_why_engine.py` | **Güncelleniyor** | `build_investigation_data()` eklendi (YAPILDI) |
| `hitl_test/gradio_chat_5why_v2.py` | **YENİ DOSYA** | Yeni akış: olay → agent immediate causes → disambiguation sorular → final analiz |
| `hitl_test/gradio_chat_5why.py` | **DOKUNULMUYOR** | Mevcut haliyle korunur |
| `agents/orchestrator.py` | **DOKUNULMUYOR** | Bozulmaz |
| `agents/overview_agent.py` | **DOKUNULMUYOR** | Sadece çağrılır |
| `agents/assessment_agent.py` | **DOKUNULMUYOR** | Sadece çağrılır |

---

## 7. Uygulama Sırası

```
[✅] ADIM 1 — five_why_engine.py: build_investigation_data() eklendi
[✅] ADIM 2 — rootcause_agent_v2.py: _append_hitl_answers() eklendi

[  ] ADIM 3 — hitl_disambiguation.py: YENİ DOSYA
     Her A/B kodu için disambiguation soruları
     Test: python -c "from hitl_test.hitl_disambiguation import get_questions; print(get_questions('B4.4'))"

[  ] ADIM 4 — gradio_chat_5why_v2.py: YENİ CHATBOT
     Akış: olay → agent immediate causes → sorular → final analiz
     State makinesi: "incident" → "analyzing_initial" → "questioning_0..N" → "analyzing_final" → "done"

[  ] ADIM 5 — Uçtan uca test
     B4.4 + "risk analizi vardı ama kontroller uygulanmadı" → D4.2 (D4.1 değil)
     B3.2 + "LOTO hiç uygulanmadı" → D4.5
     B3.2 + "Yönetim göz yumdu" → D1.9
```

---

## 8. Disambiguation → Agent Bağlantısı

Kullanıcı cevapları `investigation_data["why_answers"]` içine paketleniyor:

```python
investigation_data = {
    "description": "Hasan Yıldız iskelede düştü...",

    # Agent'ın tespit ettiği immediate causes (Adım 1'den)
    "agent_immediate_causes": [
        {"code": "B4.4", "cause_tr": "Korunmasız yükseklik..."},
        {"code": "A3.2", "cause_tr": "KKD kullanılmadı..."}
    ],

    # Kullanıcının disambiguation cevapları (Adım 2'den)
    "why_answers": [
        {
            "code": "B4.4",
            "question": "Bariyer var mıydı?",
            "answer": "Bariyer montajı yarım kalmıştı, tamamlanmamıştı",
            "hsg245_direction": "D4.2 — kontrol belirlendi ama uygulanmadı"
        },
        {
            "code": "B4.4",
            "question": "İş izni kontrol edildi mi?",
            "answer": "İzin imzalandı ama sahada kimse kontrol etmedi",
            "hsg245_direction": "D4.4 — iş izni etkisiz"
        },
        {
            "code": "B4.4",
            "question": "Risk değerlendirmesi yapılmış mıydı?",
            "answer": "Yapılmıştı, bariyer önlemi yazıyordu ama kimse uygulamadı",
            "hsg245_direction": "D4.2 — analiz var, önlem yok"
        }
    ]
}
```

Agent bu veriyi görünce:
- D4.1'i SEÇMEZ (çünkü risk analizi yapılmıştı)
- **D4.2'yi seçer** (analiz vardı, kontroller uygulanmadı)
- **D4.4'ü seçer** (iş izni etkisizdi)

---

*Dosya: `docs/INTEGRATION_PLAN_V2.md` | Proje: HSE_RCAnalysis_AgenticAI*

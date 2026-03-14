# HSE RCA — HITL + Agentic AI Entegrasyon Planı

**Tarih:** 3 Mart 2026  
**Versiyon:** 1.0  
**Hedef:** `five_why_engine.py` (kural tabanlı soru motoru) ile `RootCauseAgentV2` (LLM tabanlı derin analiz) tek bir chatbot akışında birleştirmek.

---

## 1. Mevcut Durum — İki Ayrı Yapı

### 1.1 Yapı A: Agentic Pipeline (`agents/`)
```
OverviewAgent → AssessmentAgent → RootCauseAgentV2 → SkillBasedDocxAgent
```

| Dosya | Görev | LLM? |
|-------|-------|------|
| `agents/overview_agent.py` | Olayı yapılandırır (ref_no, yer, kişi, yaralanma) | ✅ OpenRouter |
| `agents/assessment_agent.py` | Şiddet, RIDDOR, investigation level | ✅ OpenRouter |
| `agents/rootcause_agent_v2.py` | A/B → 5-Why → C/D analizi | ✅ OpenRouter |
| `agents/skillbased_docx_agent.py` | HTML + DOCX rapor üretimi | ✅ Anthropic Claude |
| `agents/knowledge_base.py` | HSG245 A/B/C/D taksonomi verisi | ❌ statik |
| `agents/orchestrator.py` | Tüm adımları sırayla çalıştırır | ❌ yönlendirici |

**Eksik:** Kullanıcı hiçbir aşamada dahil değil. Sistem olay metnini alır, tek seferde analiz eder, rapor çıkarır. Aynı olay metni her seferinde aynı (veya benzer) kök nedene gider.

---

### 1.2 Yapı B: HITL Chatbot (`hitl_test/`)
```
five_why_engine.py → gradio_chat_5why.py
```

| Dosya | Görev | LLM? |
|-------|-------|------|
| `hitl_test/five_why_engine.py` | Sabit soru ağacı, keyword branching, kök neden kodları | ❌ kural tabanlı |
| `hitl_test/gradio_chat_5why.py` | Chatbot UI, adım adım 5-Why sohbeti | ❌ sadece UI |
| `hitl_test/question_engine.py` | Kategori bazlı soru üretimi (kronoloji, PPE, eğitim...) | ❌ şablon tabanlı |
| `hitl_test/hybrid_input_processor.py` | Olay metnindeki eksiklikleri tespit eder | ❌ keyword matching |
| `hitl_test/gradio_hitl_system.py` | Eski HITL deneyi: agent'ları çağırıyor ama 5-Why bağlı değil | ✅ agent'ları çağırır |

**Eksik:** Kullanıcının cevapları sadece sabit keyword'lerle eşleştirilir. LLM analiz yok. Sonuç yüzeysel ve basit. Agent'ların derin analiz kapasitesi kullanılmıyor.

---

## 2. Problem Tanımı

```
Mevcut sorun:
┌─────────────────────────────────────────────────────────────────┐
│  gradio_chat_5why.py                                            │
│  • Kullanıcıdan 5 cevap toplar ✅                               │
│  • Keyword matching ile kök neden kodları önerir ✅             │
│  • Ama önerilen kodlar çok genel (D4.5, D1.2 gibi)             │
│  • RootCauseAgentV2'nin derin 5-Why analizi KULLANILMIYOR ❌    │
│  • OverviewAgent, AssessmentAgent KULLANILMIYOR ❌              │
│  • Sonuç: İnsan gibi yazılmış 5-Why zinciri yok ❌              │
│  • Sonuç: Senaryo bazlı farklı kök nedenler üretilemiyor ❌     │
└─────────────────────────────────────────────────────────────────┘
```

**İstenen hedef:**
- Kullanıcı chatbotta konuşurken topladığı bilgiler `RootCauseAgentV2`'ye aktarılsın
- Agent, bu spesifik cevaplara dayanarak **farklı olaylarda farklı 5-Why zincirleri** üretsin
- Sonuç hem chatbot ekranında hem HTML/DOCX raporda görünsün
- Agent yapısı **bozulmadan** sadece HITL'a entegre edilsin

---

## 3. Hedef Mimari

```
KULLANICI
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  gradio_chat_5why_v2.py  (YENİ — mevcut chat UI korunur)   │
│                                                             │
│  AŞAMA 1: Olay Toplama                                      │
│  ─────────────────────────────────────────────────────────  │
│  • Kullanıcı olay metnini yazar                             │
│  • HybridInputProcessor → eksik kategoriler tespit edilir  │
│  • OverviewAgent → part1 (yapılandırılmış olay verisi)      │
│  • AssessmentAgent → part2 (şiddet, RIDDOR, level)         │
│                                                             │
│  AŞAMA 2: Derinleştirme Soruları (HITL)                     │
│  ─────────────────────────────────────────────────────────  │
│  • five_why_engine.py → Immediate Cause menüsü              │
│  • Kullanıcı kod seçer (örn: B4.4)                         │
│  • FIVE_WHY_TREE sorularını sırayla sor (Why-1...Why-5)    │
│  • Her cevabı kaydet (state["answers"])                     │
│                                                             │
│  AŞAMA 3: Agentic Analiz                                    │
│  ─────────────────────────────────────────────────────────  │
│  • Toplanan cevapları investigation_data'ya paketle         │
│  • RootCauseAgentV2.analyze_root_causes() çağır             │
│  • Agent: kullanıcı cevaplarına göre 5-Why zinciri üretir  │
│  • Agent: her olayda FARKLI sonuçlar üretir                 │
│                                                             │
│  AŞAMA 4: Rapor                                             │
│  ─────────────────────────────────────────────────────────  │
│  • SkillBasedDocxAgent → HTML + DOCX                        │
│  • Chatbot'ta inline özet görüntülenir                      │
│  • outputs/ klasörüne kaydet                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Veri Akışı — Detaylı

### 4.1 State Objesi (Genişletilmiş)

```python
# Mevcut state (gradio_chat_5why.py):
state = {
    "step": "incident" | "cause" | "why_1..5" | "done",
    "incident": str,
    "cause_code": str,
    "questions": list,
    "answers": list,
    "directions": list,
}

# Hedef state (gradio_chat_5why_v2.py):
state = {
    # AŞAMA 1 — HITL sohbet state'i (mevcut)
    "step": "incident" | "cause" | "why_1..5" | "analyzing" | "done",
    "incident": str,
    "cause_code": str,
    "questions": list,         # five_why_engine'den gelen sorular
    "answers": list,           # kullanıcının 5 cevabı
    "directions": list,        # keyword branching sonuçları

    # AŞAMA 2 — Agent sonuçları (YENİ)
    "part1": dict | None,      # OverviewAgent sonucu
    "part2": dict | None,      # AssessmentAgent sonucu
    "part3": dict | None,      # RootCauseAgentV2 sonucu
    "report_path": str | None, # DOCX/HTML dosya yolu
}
```

---

### 4.2 investigation_data Paketi (RootCauseAgentV2'ye gönderilen)

```python
investigation_data = {
    # Temel olay bilgisi
    "description": state["incident"],
    "immediate_cause_code": state["cause_code"],
    "immediate_cause_desc": IMMEDIATE_CAUSES[state["cause_code"]],

    # Kullanıcının 5-Why cevapları (KILIT — farklılaşmayı sağlayan)
    "five_why_answers": [
        {
            "why_level": i + 1,
            "question": state["questions"][i]["soru"],
            "hsg245_focus": state["questions"][i]["hsg245"],
            "user_answer": state["answers"][i],
            "suggested_direction": state["directions"][i],  # keyword hint
        }
        for i in range(len(state["answers"]))
    ],

    # HITL'dan gelen ek bağlam
    "hitl_context": {
        "questions_asked": len(state["questions"]),
        "answers_collected": len(state["answers"]),
        "keyword_directions": [d for d in state["directions"] if d],
    }
}
```

---

### 4.3 RootCauseAgentV2 Prompt Güncelleme

`rootcause_agent_v2.py` içinde `_prepare_incident_summary()` metodu genişletilecek:

```python
# Mevcut: sadece olay metnini alır
incident_summary = incident_text

# Hedef: 5-Why cevaplarını da ekle
if investigation_data and "five_why_answers" in investigation_data:
    incident_summary += "\n\n=== HITL 5-WHY CEVAPLARI ===\n"
    for fw in investigation_data["five_why_answers"]:
        incident_summary += f"Why-{fw['why_level']}: {fw['question']}\n"
        incident_summary += f"Cevap: {fw['user_answer']}\n"
        if fw['suggested_direction']:
            incident_summary += f"Yön İpucu: {fw['suggested_direction']}\n"
        incident_summary += "\n"
```

Bu sayede agent:
- Aynı B4.4 kodu için → "LOTO yoktu" cevabı → D4.5 kök neden
- Aynı B4.4 kodu için → "Yönetim baskısı vardı" cevabı → D1.4 kök neden
- **Her seferinde farklı**, gerçek cevaplara dayalı kök neden üretir.

---

## 5. Yapılacaklar — Adım Adım

### ADIM 1: `investigation_data` paketleme fonksiyonu
**Dosya:** `hitl_test/five_why_engine.py`  
**Değişiklik:** Yeni yardımcı fonksiyon ekle

```python
def build_investigation_data(state: dict) -> dict:
    """
    Chatbot state'inden RootCauseAgentV2'ye gönderilecek veri paketini oluşturur.
    Mevcut five_why_engine koduna dokunulmaz, sadece ek fonksiyon.
    """
    answers = state.get("answers", [])
    questions = state.get("questions", [])
    directions = state.get("directions", [])

    return {
        "description": state.get("incident", ""),
        "immediate_cause_code": state.get("cause_code", ""),
        "immediate_cause_desc": IMMEDIATE_CAUSES.get(state.get("cause_code", ""), ""),
        "five_why_answers": [
            {
                "why_level": i + 1,
                "question": questions[i]["soru"] if i < len(questions) else "",
                "hsg245_focus": questions[i]["hsg245"] if i < len(questions) else "",
                "user_answer": answers[i] if i < len(answers) else "",
                "suggested_direction": directions[i] if i < len(directions) else "",
            }
            for i in range(max(len(answers), len(questions)))
        ],
        "hitl_context": {
            "questions_asked": len(questions),
            "answers_collected": len(answers),
            "keyword_directions": [d for d in directions if d],
        }
    }
```

**Test:** `python -c "from hitl_test.five_why_engine import build_investigation_data; print('OK')"`

---

### ADIM 2: `_prepare_incident_summary` güncelleme
**Dosya:** `agents/rootcause_agent_v2.py`  
**Değişiklik:** Mevcut metoda HITL cevaplarını dahil et

```python
def _prepare_incident_summary(self, part1_data, part2_data, investigation_data=None):
    # ... mevcut kod aynen kalır ...

    # YENİ: HITL 5-Why cevaplarını ekle
    if investigation_data and "five_why_answers" in investigation_data:
        summary += "\n\n=== KULLANICI 5-WHY CEVAPLARI (HITL) ===\n"
        summary += "Bu cevaplar soruşturma sırasında kullanıcıdan toplanan gerçek bilgilerdir.\n"
        summary += "Kök neden analizini BU CEVAPLARA GÖRE yap. Genel varsayım kullanma.\n\n"
        for fw in investigation_data["five_why_answers"]:
            summary += f"Why-{fw['why_level']} Sorusu: {fw['question']}\n"
            summary += f"Kullanıcı Cevabı: {fw['user_answer']}\n"
            if fw.get("suggested_direction"):
                summary += f"HSG245 Yönü: {fw['suggested_direction']}\n"
            summary += "\n"

    return summary
```

**Test:** `python -m pytest tests/ -k "rootcause" -v`

---

### ADIM 3: `gradio_chat_5why_v2.py` — Ana Chatbot (YENİ DOSYA)
**Dosya:** `hitl_test/gradio_chat_5why_v2.py`  
**Değişiklik:** Mevcut `gradio_chat_5why.py` korunur, yeni dosya oluşturulur

Akış değişikliği:

```python
# Mevcut step makinesi:
"incident" → "cause" → "why_1" → ... → "why_5" → "done"

# Yeni step makinesi:
"incident" → "cause" → "why_1" → ... → "why_5" → "analyzing" → "done"
                                                        │
                                                        ▼
                                              [OverviewAgent]
                                              [AssessmentAgent]
                                              [RootCauseAgentV2]
                                              [SkillBasedDocxAgent]
```

```python
# why_5 cevabı alındıktan sonra:
if next_why > len(questions):
    state["step"] = "analyzing"
    history.append(_bot("⏳ Cevaplarınız analiz ediliyor, lütfen bekleyin..."))
    
    # Background thread veya yield ile:
    result = run_agentic_analysis(state)  # YENİ FONKSİYON
    state["part3"] = result["part3"]
    state["report_path"] = result["report_path"]
    state["step"] = "done"
    
    history.append(_bot(format_agent_result(result)))  # YENİ FORMAT FONKSİYONU
```

---

### ADIM 4: `run_agentic_analysis()` fonksiyonu
**Dosya:** `hitl_test/gradio_chat_5why_v2.py`

```python
def run_agentic_analysis(state: dict) -> dict:
    """
    Chatbot state'inden agent pipeline'ını çalıştırır.
    Agent yapısına dokunmaz, sadece çağırır.
    """
    from agents.overview_agent import OverviewAgent
    from agents.assessment_agent import AssessmentAgent
    from agents.rootcause_agent_v2 import RootCauseAgentV2
    from agents.skillbased_docx_agent import SkillBasedDocxAgent
    from hitl_test.five_why_engine import build_investigation_data

    # 1. Olay verisini hazırla
    incident_dict = {"description": state["incident"]}

    # 2. Overview
    part1 = OverviewAgent().process_initial_report(incident_dict)

    # 3. Assessment
    part2 = AssessmentAgent().assess_incident(part1, incident_dict)

    # 4. investigation_data paketini oluştur (HITL cevapları dahil)
    investigation_data = build_investigation_data(state)

    # 5. Root Cause (HITL cevaplarıyla birlikte)
    part3 = RootCauseAgentV2().analyze_root_causes(
        part1_data=part1,
        part2_data=part2,
        investigation_data=investigation_data
    )

    # 6. Rapor (opsiyonel — API key varsa)
    report_path = None
    try:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"outputs/hitl_{timestamp}.docx"
        report_data = {"part1": part1, "part2": part2, "part3_rca": part3}
        report_path = SkillBasedDocxAgent().generate_report(report_data, output_file)
    except Exception as e:
        print(f"⚠️ Rapor üretimi atlandı: {e}")

    return {
        "part1": part1,
        "part2": part2,
        "part3": part3,
        "report_path": report_path,
    }
```

---

### ADIM 5: `format_agent_result()` — Chatbot Sonuç Formatı
**Dosya:** `hitl_test/gradio_chat_5why_v2.py`

Agent sonucunu chatbot mesajına dönüştürür:

```python
def format_agent_result(result: dict) -> str:
    """Agent sonucunu chatbot mesajı formatına çevirir"""
    part1 = result.get("part1", {})
    part2 = result.get("part2", {})
    part3 = result.get("part3", {})

    lines = [
        "---",
        "## ✅ AI Analizi Tamamlandı",
        "",
        f"📋 **Olay Ref:** `{part1.get('ref_no', 'N/A')}`",
        f"⚠️ **Şiddet:** {part2.get('actual_potential_harm', 'N/A')}",
        f"📊 **İnceleme Seviyesi:** {part2.get('investigation_level', 'N/A')}",
        "",
        "### 🌿 5-Why Zincirleri (AI Analizi)",
    ]

    for i, branch in enumerate(part3.get("analysis_branches", []), 1):
        imm = branch.get("immediate_cause", {})
        lines.append(f"\n**Dal {i}:** `{imm.get('code')}` — {imm.get('cause_tr', '')}")
        chain = branch.get("five_why_chain", {})
        for why in chain.get("whys", []):
            lines.append(f"- **Why-{why['level']}:** {why.get('answer_tr', '')}")
        root = chain.get("root_cause", {})
        lines.append(f"- 🎯 **Kök Neden:** `{root.get('code')}` {root.get('root_cause_title', '')}")

    lines.append("")
    lines.append("### 🟣 Final Kök Nedenler")
    for rc in part3.get("final_root_causes", []):
        lines.append(f"- **`{rc.get('root_cause_code')}`** {rc.get('root_cause_title')}")
        lines.append(f"  > {rc.get('description', '')[:150]}...")

    if result.get("report_path"):
        lines.append("")
        lines.append(f"📄 **Rapor:** `{result['report_path']}`")

    lines.append("")
    lines.append("---")
    lines.append("🔄 Yeni analiz için `yeni` yazın veya **Temizle** butonuna basın.")
    return "\n".join(lines)
```

---

## 6. Dosya Değişiklik Özeti

| Dosya | Durum | Ne Değişiyor |
|-------|-------|--------------|
| `agents/rootcause_agent_v2.py` | **Güncelleniyor** | `_prepare_incident_summary()` — HITL cevaplarını prompt'a ekle |
| `hitl_test/five_why_engine.py` | **Güncelleniyor** | `build_investigation_data()` fonksiyonu ekle |
| `hitl_test/gradio_chat_5why_v2.py` | **YENİ DOSYA** | Mevcut chatbot + agentic analiz entegrasyonu |
| `hitl_test/gradio_chat_5why.py` | **DOKUNULMUYOR** | Mevcut haliyle korunur (fallback) |
| `agents/orchestrator.py` | **DOKUNULMUYOR** | Mevcut pipeline bozulmaz |
| `agents/overview_agent.py` | **DOKUNULMUYOR** | Sadece çağrılır |
| `agents/assessment_agent.py` | **DOKUNULMUYOR** | Sadece çağrılır |
| `agents/skillbased_docx_agent.py` | **DOKUNULMUYOR** | Sadece çağrılır |

---

## 7. Test Planı

### Test 1 — five_why_engine.py eklenti
```bash
cd /Users/selcuk/Desktop/HSE_RCAnalysis_AgenticAI-main
source .venv/bin/activate
python -c "
from hitl_test.five_why_engine import build_investigation_data
state = {
    'incident': 'Elektrik çarptı',
    'cause_code': 'B3.2',
    'questions': [{'soru': 'LOTO var mıydı?', 'hsg245': 'D4.5'}],
    'answers': ['LOTO hiç uygulanmadı'],
    'directions': ['→ D4.5 kök neden'],
}
data = build_investigation_data(state)
print('OK:', data['immediate_cause_code'], '|', data['five_why_answers'][0]['user_answer'])
"
```
Beklenen: `OK: B3.2 | LOTO hiç uygulanmadı`

---

### Test 2 — rootcause_agent_v2.py HITL entegrasyon
```bash
python -c "
import os
os.environ.setdefault('OPENROUTER_API_KEY', 'test')
from agents.rootcause_agent_v2 import RootCauseAgentV2
agent = RootCauseAgentV2()
summary = agent._prepare_incident_summary(
    {'incident_type': 'Elektrik kazası'},
    {'actual_potential_harm': 'Serious'},
    {
        'description': 'Elektrik çarptı',
        'five_why_answers': [
            {'why_level': 1, 'question': 'LOTO var mı?', 'hsg245_focus': 'D4.5',
             'user_answer': 'LOTO hiç uygulanmamış', 'suggested_direction': '→ D4.5'}
        ]
    }
)
print('HITL bölümü var mı:', 'HITL' in summary)
print(summary[-300:])
"
```
Beklenen: `HITL bölümü var mı: True`

---

### Test 3 — Uçtan uca chatbot akışı (API KEY gerekir)
```bash
python -c "
import sys; sys.path.insert(0, '.')
from hitl_test.gradio_chat_5why_v2 import chat, init_state, _bot

state = init_state()
history = [_bot('Merhaba')]

# Olay
history, state, _ = chat('18 Şubat 2026 Hasan Yıldız iskelede düştü', history, state)
# Cause seçimi
history, state, _ = chat('17', history, state)  # B4.4
# 5 Why cevabı
history, state, _ = chat('Bariyer yoktu, denetim eksikti', history, state)
history, state, _ = chat('İş izni alınmamış', history, state)
history, state, _ = chat('Yönetim baskısı vardı, hızlı teslim gerekiyordu', history, state)
history, state, _ = chat('Eğitim 3 ay önceydi, tazeleme yok', history, state)
history, state, _ = chat('Hiç kurumsal prosedür yazılmamış', history, state)

# Son mesaj AI analiz sonucu olmalı
last = history[-1]['content']
print('Kök neden bulundu mu:', 'Kök Neden' in last or 'root_cause' in last.lower())
print('Agent analizi var mı:', 'AI Analizi' in last or 'analysis_branches' in str(state.get('part3', {})))
"
```
Beklenen: `Kök neden bulundu mu: True`

---

### Test 4 — İki farklı senaryo → farklı kök neden
```bash
# Senaryo A: Üretim baskısı
python hitl_test/test_integration_scenario_a.py

# Senaryo B: Eğitim eksikliği  
python hitl_test/test_integration_scenario_b.py

# Karşılaştır: her iki senaryodaki root_cause_code'lar farklı olmalı
```

---

## 8. Çalıştırma

### Mevcut chatbot (kural tabanlı, API gerektirmez):
```bash
source .venv/bin/activate
python hitl_test/gradio_chat_5why.py
# → http://127.0.0.1:7860
```

### Yeni entegre chatbot (LLM analiz, OPENROUTER_API_KEY gerekir):
```bash
source .venv/bin/activate
python hitl_test/gradio_chat_5why_v2.py
# → http://127.0.0.1:7861
```

---

## 9. Riskler ve Önlemler

| Risk | Önlem |
|------|-------|
| API çağrısı uzun sürebilir (10-30sn) | `"analyzing"` adımında spinner mesajı + `gr.Chatbot` yield pattern |
| API key yoksa chatbot çöker | `run_agentic_analysis()` try/except ile sarılır, API yoksa kural tabanlı sonuç döner |
| Agent yapısı bozulabilir | Tüm agent dosyaları dokunulmadan kalır, sadece `_prepare_incident_summary` güncellenir |
| RootCauseAgentV2 HITL verisini görmeyebilir | `investigation_data["five_why_answers"]` key kontrolü eklenir |
| Rapor üretimi (Anthropic) başarısız olabilir | `SkillBasedDocxAgent` çağrısı ayrı try/except'te, başarısız olursa raporsuz devam edilir |

---

## 10. Uygulama Sırası

```
[ ] ADIM 1 — five_why_engine.py: build_investigation_data() ekle
         → Test: python -c "from hitl_test.five_why_engine import build_investigation_data"

[ ] ADIM 2 — rootcause_agent_v2.py: _prepare_incident_summary() güncelle  
         → Test: HITL verisi prompt'a giriyor mu kontrol et

[ ] ADIM 3 — gradio_chat_5why_v2.py: Yeni dosya oluştur
         → Test: Import OK + state makinesi çalışıyor mu

[ ] ADIM 4 — Uçtan uca test (API ile)
         → B3.2 + "LOTO yok" → D4.5 kök neden
         → B3.2 + "Eğitim eksik" → D3.1 kök neden
         → İki farklı sonuç üretilmeli

[ ] ADIM 5 — Rapor entegrasyonu
         → SkillBasedDocxAgent chatbot akışına bağla
```

---

*Dosya: `docs/INTEGRATION_PLAN.md` | Proje: HSE_RCAnalysis_AgenticAI*

# V3.2 — olay-zarar 5-Why paketi (ACTIVE — production varsayılan)

Parallel stack; **production varsayılan = V3.2** (`ROOTCAUSE_AGENT_VERSION=3.2`).

## Neden tüm `rootcause_agent_v3_1.py` burada değil?

`rootcause_agent_v3_1.py` (~2300 satır) tek dosyada **7 katman** bir arada:

| Katman | V3.1 | V3.2 dosyası |
|--------|------|----------------|
| Doğrudan neden (A/B) | `ImmediateCauseFinder` | `v31_bridge.py` → miras |
| **5-Why zinciri** | `WhyChain` | **`why_chain_v3_2.py`** ← tek farklı çekirdek |
| W1 kalite kuralları | `why_chain_quality.py` | **`why_chain_quality_v3_2.py`** |
| Kök neden agent | `RootCauseAgentV3_1` | **`rootcause_agent_v3_2.py`** (miras + WhyChainV32) |
| Rapor LLM | `skillbased_docx_agent.py` | **`skillbased_docx_agent_v3_2.py`** |
| Rapor why pin | — | **`report_why_chain_v3_2.py`** |
| Decision tree | `decision_tree_mermaid.py` | **`decision_tree_v3_2.py`** |
| Uçtan uca test | — | **`pipeline_v3_2.py`** |

2329 satırın kopyalanması bakım riski yaratır; V3.2 **composition** ile V3.1'i genişletir.

## V3.1 hatası (V3.2 ile düzeltildi)

`build_event_why1_question` ilk cümleden faaliyet sorusu üretir:

```
YANLIŞ: Neden … segment strand halat montaj meydana geldi?
DOĞRU:  Neden Garcia 3,8 metre yükseklikten düşerek ağır yaralandı?
```

## Trainset akış

```
NEDEN 1 — Ortak olay-zarar sorusu → cevap: dal A/B (BARSEL)
NEDEN 2   — W1 A/B cevabına neden
NEDEN 3–5 — LLM → C/D kök
```

## Aktivasyon

Varsayılan (kod + Railway):

```env
ROOTCAUSE_AGENT_VERSION=3.2
OPENROUTER_DSPY_MODEL=anthropic/claude-haiku-4.5
```

V3.1'e dönmek için: `ROOTCAUSE_AGENT_VERSION=3.1`

## Dosya listesi

```
agents/v3_2/
├── __init__.py
├── README.md
├── v31_bridge.py                 # V3.1 paylaşılan bileşen re-export
├── why_chain_quality_v3_2.py     # W1 soru + A/B cevap
├── why_chain_v3_2.py             # WhyChainV32.forward
├── rootcause_agent_v3_2.py       # RootCauseAgentV3_2
├── report_why_chain_v3_2.py      # HTML/DOCX why_chain pin
├── skillbased_docx_agent_v3_2.py # Rapor LLM + pin (LLM ezmesini engeller)
├── decision_tree_v3_2.py         # Ağaç W1 trainset
└── pipeline_v3_2.py              # analyze + report test girişi
```

## skillbased_docx uyumu

Production `skillbased_docx_agent.py` V3.1 agent + **pin yok** → LLM why_chain'i ezebilir.

V3.2 pipeline **`SkillBasedDocxAgentV32`** kullanır:
- merge sonrası `pin_agent_why_chains_to_report_v32`
- fallback'te de pin
- `CONTENT_SYSTEM_PROMPT_V32`: LLM'e why_chain yazdırma

## Kullanım

```python
from agents.v3_2 import create_v3_2_agent, SkillBasedDocxAgentV32
from agents.v3_2.pipeline_v3_2 import run_v3_2_analysis_and_report

agent = create_v3_2_agent(use_rag=True)
part3 = agent.analyze_root_causes(part1, part2, inv)

docx = SkillBasedDocxAgentV32()
docx.generate_report({"part1": part1, "part2": part2, "part3_rca": part3}, "out/report.docx")
```

## Test

```bash
pytest tests/test_rootcause_agent_v3_2.py tests/test_report_why_chain_v3_2.py -v
```

## Aktivasyon (ileride)

`ROOTCAUSE_AGENT_VERSION=3.2` + orchestrator + rapor agent seçimi.

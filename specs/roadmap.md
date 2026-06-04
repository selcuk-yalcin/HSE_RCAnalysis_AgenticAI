# Execution Roadmap (Active Backlog)

Tamamlanan maddeler (✅) **`specs/roadmap-archive.md`** içinde — git geçmişiyle birlikte referans.  
Bu dosya yalnızca **açık işleri** takip eder.

---

## Maliyet / kalite — OpenRouter (P1.21)

**Gözlem:** Tek rapor ~50+ istek, ~300K token, ~$0.45–0.50 (Haiku) — 4 dal × 5-Why × ChainOfThought + BranchCritic + HITL LLM.

**Kaliteyi düşürmez;** fazla istek = maliyet + gecikme. Çözüm: maliyet profili (varsayılan **`balanced`**).

| Profil | Env | ~İstek/rapor | Davranış |
|--------|-----|--------------|----------|
| **balanced** | `ROOTCAUSE_COST_PROFILE=balanced` (varsayılan) | ~25–35 | Predict 5-Why, critic×1, max 3 dal, HITL rule-based |
| **economy** | `ROOTCAUSE_COST_PROFILE=economy` | ~15–20 | Critic kapalı, max 2 dal |
| **quality** | `ROOTCAUSE_COST_PROFILE=quality` | ~50+ | Eski davranış (CoT + critic×3 + HITL LLM) |

Railway **Agents + worker:**

```
ROOTCAUSE_COST_PROFILE=balanced
```

Kod: `agents/rca_cost_profile.py`, `agents/rootcause_agent_v3_1.py`, `tasks/pipeline_tasks.py`

---

## P1.20 BARSEL RAG — kalan

| Adım | Durum | İş |
|------|--------|-----|
| **R2** | ⏳ | Parser QA: 156 kod, keywords/typical_problems doluluk |
| **R6b** | ⏳ | HITL: `hitl_disambiguation_bank` + `QuestionEngine` taxonomy_gap → BARSEL |
| **R9** | ⏳ | BARSEL sentetik dataset (iyi/kötü) |
| **R10** | ⏳ | MIPROv2 + A/B + promote |
| **OPS-E4/E5** | ⏳ | Railway explicit env doğrulama |
| **OPS-E7–E10** | ⏳ | verify one-off, HF_TOKEN, TZ, yerel ST venv |

**Production env (API + worker):**

```
TAXONOMY_EMBEDDING_BACKEND=sentence_transformers
TAXONOMY_COLLECTION=taxonomy_barsel
HITL_USE_BARSEL=1
ROOTCAUSE_COST_PROFILE=balanced
```

---

## Öncelikli platform (kısa liste)

### Güvenlik / tenant (P1.18)
- ⏳ JWT doğrulama (Kinde); sahte `X-User-ID` kapatma
- ⏳ Rate limiting (pipeline, HITL, report)
- ⏳ Audit log koleksiyonu

### HITL (P0.2 kalan)
- ⏳ HITL log persist (training)
- ⏳ BARSEL disambiguation bank migrasyonu (R6b)

### Ürün
- ⏳ Dal kurulum ekranı (P1.12) — kullanıcı onayı → pipeline
- ⏳ Multimodal ekler (P1.13)
- ⏳ `tenant_config` + plan kotası DB (P1.17)

### Kurumsal LLM
- ⏳ [`roadmap-ovh-mistral.md`](roadmap-ovh-mistral.md) — veri egresyonu / sovereign path

---

## Referans

| Dosya | İçerik |
|-------|--------|
| [`roadmap-archive.md`](roadmap-archive.md) | Tam geçmiş roadmap (✅ maddeler dahil) |
| [`plan.md`](plan.md) | Ürün + mimari |
| [`tech-stack.md`](tech-stack.md) | Runtime kısıtları |
| [`TODO.md`](../TODO.md) | Detaylı teknik görevler |

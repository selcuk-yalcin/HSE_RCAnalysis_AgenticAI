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
| **R6b** | ✅ | HITL tam BARSEL: disambiguation, taxonomy_gap, why-probe code-specific (`HITL_USE_BARSEL=1`) |
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
- ⏳ **HITL kök neden aday netleştirme (C/D `typical_problems`)** — aşağıda P1.22

---

## P1.22 HITL — kök neden çeşitlendirme (C/D probe)

**Sorun:** 5-Why sonunda kök nedenler sık sık **D4.x (risk değerlendirmesi / iş planlama)** bandına toplanıyor. Mevcut HITL yalnızca **A/B doğrudan neden** probe’u yapıyor (`why_level=1`, `codes_for_why_level` band değiştirmiyor); C/D `typical_problems` kök neden seçimine bağlanmıyor (`affirmed_typical_problems` yalnızca level-5 + Evet).

**Hedef:** HITL’e A/B probe’larından sonra (veya dal başına ek faz) **kök neden aday netleştirme** eklemek; rapor çeşitliliğini artırmak, jenerik D4.1 tuzağını azaltmak.

| Adım | Durum | İş |
|------|--------|-----|
| **RC1** | ⏳ | `codes_for_why_level` / yeni `codes_for_root_probe`: olay metnine göre Mongo RAG ile **2–4 C/D aday kodu** (relevance eşiği; olayla alakasız kodları eleme) |
| **RC2** | ⏳ | Her aday için `typical_problems` → mevcut probe şablonu (`probe_question_for_type`, `probe_context`); boşsa `definition` ilk cümle fallback |
| **RC3** | ⏳ | HITL cevap semantiği: **Evet** → `affirmed_typical_problems` + dal bağlamı; **Hayır/Bilinmiyor** → `forbidden_root_codes` / RAG exclusion (dal ve global) |
| **RC4** | ⏳ | `rootcause_agent_v3_1`: forbidden + affirmed sinyallerini 5-Why (Why-4/5) ve `derive_root_cause_from_why5` zincirine bağla; level-5-only kısıtını kaldır |
| **RC5** | ⏳ | Frontend (`ChatInterface.jsx`): `why_probe` fazı — A/B immediate probe sonrası **root_probe** modu; cap (`MAX_ROOT_PROBE_ANSWERS`); Türkçe UI etiketleri |
| **RC6** | ⏳ | Testler: depo/yaya–forklift senaryosunda D4.1 tekrarı azalır; D4.9/D5/D1 gibi spesifik kodlar mümkün; Hayır → kod dışlanır |
| **RC7** | ⏳ | `ROOTCAUSE_COST_PROFILE=balanced` ile uyum: rule-based probe öncelikli; LLM probe context opsiyonel (`HITL_LLM_PROBE_CONTEXT`) |

**Kabul kriterleri:**
- Aynı olayda 3+ dal sonrası kök neden başlıklarında **aynı D4.1/D4.2 teması** baskın olmamalı (branch critic + forbidden ile).
- Kullanıcı D8.6 tipik problemine **Hayır** derse, o kod ilgili dalda kök neden olarak seçilmemeli.
- Mevcut A/B immediate HITL akışı bozulmamalı; root probe ek faz olarak çalışmalı.

**Kod dokunuşu (planlı):** `agents/hitl_question_service.py`, `agents/barsel_taxonomy.py`, `agents/rootcause_agent_v3_1.py`, `admin_pan/Admin/src/rca-frontend/components/ChatInterface.jsx`, `api/main.py`, `tests/test_mongo_why_flow.py` (+ yeni root-probe testleri).

**Env (değişiklik yok — mevcut):** `HITL_USE_BARSEL=1`, `TAXONOMY_COLLECTION=taxonomy_barsel`, `HITL_PROBE_MIN_RELEVANCE=0.03`

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

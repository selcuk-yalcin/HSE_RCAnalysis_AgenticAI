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
| **R9** | ✅ (v1) | BARSEL/küratörlü sektör dataset (iyi/kötü) — `build_curated_sector_dataset.py`, 30 örnek train/dev/test |
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
| **RC1** | 🔨 | `barsel_taxonomy.root_cause_candidate_codes(incident, immediate_code, retriever, max_codes=6, max_per_group=2)`: C+D'den relevance ile aday kodlar; **D-grup çeşitliliği** (aynı D4 grubundan ≤2), gruplara yayılım |
| **RC2** | 🔨 | `hitl_question_service.next_root_cause_probe_questions(...)`: `build_why_probe_question_pool(candidate_codes=...)` ile her aday için `typical_problems` probe'u; şablon `probe_question_for_type('typical_problem')`; `definition` fallback |
| **RC3** | 🔨 | Cevap semantiği: `probe_answer_affirms_fit` (Evet) → affirm; yeni `probe_answer_denies_fit` (kesin Hayır) → forbidden; belirsiz/"bilmiyorum" → etkisiz (yanlış dışlama önlenir) |
| **RC4** | 🔨 | `rootcause_agent_v3_1.analyze_root_causes`: `root_cause_probe_answers` → `forbidden_from_hitl` (used_root_codes ile **birleşir**) + `affirmed_root_codes`/typical_problems; `identify_branch`'e affirmed bias (Why≥4 "TERCİH" hint + `derive_root_cause_from_why5` affirmed) |
| **RC5** | ✅ | Frontend (`ChatInterface.jsx`): A/B immediate probe sonrası `rootcause_probe` fazı (`MAX_ROOT_PROBE_ANSWERS=6`); `hsg245Api.js`+proxy `hsg245.js` `root_cause_probe_answers`/`mode` iletir; Türkçe UI |
| **RC6** | 🔨 | Testler: `root_cause_candidate_codes` C+D + grup çeşitliliği; "Hayır"→forbidden, "Evet"→affirmed, belirsiz→etkisiz |
| **RC7** | ✅ | `balanced` uyum: rule-based probe öncelikli; LLM probe context opsiyonel (`HITL_LLM_PROBE_CONTEXT`, varsayılan kapalı) |

**Kabul kriterleri:**
- Aynı olayda 3+ dal sonrası kök neden başlıklarında **aynı D4.1/D4.2 teması** baskın olmamalı (branch critic + forbidden ile).
- Kullanıcı D8.6 tipik problemine **Hayır** derse, o kod ilgili dalda kök neden olarak seçilmemeli.
- Mevcut A/B immediate HITL akışı bozulmamalı; root probe ek faz olarak çalışmalı.

**Kod dokunuşu (planlı):** `agents/hitl_question_service.py`, `agents/barsel_taxonomy.py`, `agents/rootcause_agent_v3_1.py`, `admin_pan/Admin/src/rca-frontend/components/ChatInterface.jsx`, `api/main.py`, `tests/test_mongo_why_flow.py` (+ yeni root-probe testleri).

**Env (değişiklik yok — mevcut):** `HITL_USE_BARSEL=1`, `TAXONOMY_COLLECTION=taxonomy_barsel`, `HITL_PROBE_MIN_RELEVANCE=0.03`

---

## P1.23 5-Why zincir kalitesi — kök neden / zincir tutarlılığı

**Neden hiyerarşisi (gerçek kök):** Rapor sorunları birbirine bağlı —

```
_try_snap_to_taxonomy() → cause_tr'yi W5'ten koparıp BARSEL başlığıyla eziyor
        ↓ Kök neden etiketi W5 ile uyuşmuyor (S2)
        ↓ LLM W5'i "anlamsız" görüp sonraki dallarda aynı şeyi yazıyor (S3)
        ↓ W1 zaten circularity içeriyorsa zincir başından kırık (S1)
```

**Değerlendirme (kod doğrulandı):** Görev 2 köktür → önce yapılır. Görev 4 mevcut "kod gösterme" tasarımıyla çelişir → opsiyonel/onaylı.

| Görev | Durum | Değer | İş |
|-------|--------|-------|-----|
| **G2** | ✅ | Yüksek | `snap_to_barsel_taxonomy`: `cause_tr`'yi BARSEL başlığı yerine **W5 ilk cümlesinden** türet (`_chain_root_label_from_narrative`); BARSEL kodu+başlık `standard_title_tr`'de kalır; `enrich_root_cause_from_taxonomy` zincir etiketini ezmez. `derive_root_cause_from_why5`: W5↔resmi başlık Jaccard **< 0.08** (`SNAP_ROOT_AUDIT_MIN`) → `snap_overridden`+override (mevcut 0.12 snap-reject korunur) |
| **G1** | ✅ | Orta-Yüksek | `build_why1_question`: "X neden oldu?" → "X hangi alt mekanizmayla gerçekleşti?". W1 cevabı `immediate_cause` ile Jaccard **> 0.55** ise tek retry (circularity engeli) |
| **G3** | ✅ | Orta | `_collapse_redundant_branches` threshold 0.68→**0.55** + aynı BARSEL kodu reddi (mevcut); BranchCritic 0.25→**0.18**; collapse **W3-W5 derinliğine** bakar (`_deep_chain_fingerprint`); `branch_diversity_angle(used_codes=...)` D4 kullanıldıysa risk açısını atlar. **Min 2 dal floor** |
| **G5** | ✅ | Orta | `shared/chain_audit_store.py` → her analizden sonra MongoDB `chain_audit` koleksiyonuna **snap audit + chain_quality skoru** yazar (best-effort; `CHAIN_AUDIT_ENABLED`, MONGODB_URI yoksa atlar) |
| **G4** | ✅ (opt-out) | Düşük (çelişki) | HTML `.why-code` rozeti — **varsayılan KAPALI** (`REPORT_SHOW_WHY_CODES=0`). Mevcut `strip_hse_codes` tasarımı korunur; env=1 ile yapısal rozet eklenir (narrative'e kod gömülmez). Açılması için ürün onayı |

**Kabul kriterleri:**
- Kök neden etiketi (cause_tr) ilgili dalın W5 cevabıyla anlamsal olarak örtüşmeli (Jaccard ≥ 0.08).
- 4 dallı analizde kök neden başlıkları **aynı D4.x temasında** toplanmamalı; en az 2 ayrık dal kalmalı.
- W1 sorusu doğrudan nedeni tekrar etmemeli (circularity yok).
- Snap override ve düşük chain_quality vakaları audit koleksiyonuna düşmeli.

**Kod dokunuşu (planlı):** `agents/barsel_taxonomy.py`, `agents/why_chain_quality.py`, `agents/rootcause_agent_v3_1.py`, `agents/branch_critic.py`, `agents/skillbased_docx_agent.py`, `shared/` (yeni audit store), `tests/test_why_chain_quality.py` (+ yeni snap/dedupe testleri).

**Sıra:** G2 → G1 → G3 → G5 → G4 (opsiyonel).

## P1.24 5-Why zincir kayması — Why-1 = olay sorusu (ilk iterasyon) ✅ → P1.26 ile güncellendi

**Tarihçe:** İlk kaydırma (P1.24): W1 olay sorusu + doğrudan neden cevabı; W2 alt mekanizma şablonu; 4.1'de başlangıç+doğrudan neden paragrafı.

**Güncel durum (commit `98940ca`):** Klasik 5-Why'e geçildi — bkz. **P1.26**. P1.24 satırlarındaki W2 alt-mekanizma ve 4.1 tekrarı kaldırıldı; rapor LLM kilidi (P1.26) hâlâ eksik.

| İş | Durum | Detay |
|----|--------|-------|
| W1 deterministik (agent) | ✅ | `WhyChain.forward` level 1: `build_event_why1_question` + `immediate_cause_sentence(cause_tr)` |
| W2 klasik soru (agent) | ✅ | `build_direct_cause_why2_question` — "Neden [doğrudan neden]?" |
| 4.1 tekrar bölümü | ✅ kaldırıldı | `_build_branches` / `_html_branches`: yalnızca 5-Why tablosu |
| Rapor why_chain kilidi | ✅ P1.26 | Merge sonrası agent zinciri pinlenir |

**Kod dokunuşu (agent):** `agents/why_chain_quality.py`, `agents/rootcause_agent_v3_1.py`, `tests/test_why_chain_quality.py`, `agents/decision_tree_mermaid.py`.

---

## P1.26 Klasik 5-Why + rapor zincir kilidi ✅

**Hedef yapı (tüm dallarda):**

```
NEDEN 1 — Olay sorusu (ortak, olay metninden) → Cevap: A/B doğrudan neden (kısa, meta etiket yok)
NEDEN 2 — "Neden [doğrudan neden]?" → LLM alt neden
NEDEN 3–5 — Önceki cevaba why → NEDEN 5 / kök neden kutusu: C/D kök neden
```

**Gözlem (INC-20260613-181437):** Agent doğru `immediate_cause` + `why_chain` üretse bile `_generate_content_with_claude` → `_merge_with_fallback_content` LLM'in dolu `branches[].why_chain` çıktısını koruyor; NEDEN 1 dal bazlı/uzun, bazı dallar 4 adımda kalıyor.

### Kod haritası — kim ne üretiyor / kim yazıyor

| Aşama | Dosya | Sınıf / fonksiyon | Çıktı |
|-------|--------|-------------------|--------|
| **1. Doğrudan neden (A/B)** | `agents/rootcause_agent_v3_1.py` | `ImmediateCauseFinder.forward` | `causes[]`: `{code, cause_tr, evidence_tr, category_type}` |
| BARSEL hizalama | `agents/barsel_taxonomy.py` | `snap_immediate_cause_to_barsel` | Resmi A/B kod + başlık |
| Dedupe / limit | `agents/rootcause_agent_v3_1.py` | `_dedupe_similar_immediate_causes`, `_effective_branch_limit` | Dal sayısı (2–5) |
| **2. 5-Why zinciri** | `agents/rootcause_agent_v3_1.py` | `WhyChain.forward` | `whys[]` (5 adım) |
| W1 soru | `agents/why_chain_quality.py` | `build_event_why1_question` | Olaydan "Neden … meydana geldi?" |
| W1 cevap | `agents/why_chain_quality.py` | `immediate_cause_sentence` | `immediate_cause.cause_tr` (kısa) |
| W2 soru | `agents/why_chain_quality.py` | `build_direct_cause_why2_question` | "Neden [doğrudan neden]?" |
| W3–5 | `agents/rootcause_agent_v3_1.py` | `WhyChain` → `why_question` / `why_answer` (DSPy) | LLM soru-cevap |
| **3. Kök neden (C/D)** | `agents/why_chain_quality.py` | `derive_root_cause_from_why5` | `{code, cause_tr, explanation_tr, …}` |
| BARSEL snap | `agents/barsel_taxonomy.py` | `snap_to_barsel_taxonomy`, `enrich_root_cause_from_taxonomy` | Kök kod + açıklama |
| Validator | `agents/rootcause_agent_v3_1.py` | `RootCauseValidator` (DSPy) | C/D band doğrulama |
| **4. Dal paketi** | `agents/rootcause_agent_v3_1.py` | `RootCauseAgentV3_1.analyze_root_causes` | `part3_rca.analysis_branches[]` → `{immediate_cause, why_chain, root_cause}` |
| Dal eleştirisi | `agents/branch_critic.py` | `BranchCritic.review` | Tekrarlayan kök/dal → regenerate |
| Pipeline | `agents/orchestrator.py`, `tasks/pipeline_tasks.py` | `analyze_root_causes` çağrısı | `investigation_data.part3_rca` |
| **5. Rapor ham → JSON** | `agents/skillbased_docx_agent.py` | `_build_deterministic_fallback_content` | Agent `why_chain` + `root_cause` kopyası (pinned) |
| **6. Rapor LLM** | `agents/skillbased_docx_agent.py` | `_generate_content_with_claude` | Tüm rapor JSON (executive summary, dallar, …) |
| Merge | `agents/skillbased_docx_agent.py` | `_merge_with_fallback_content` | LLM dolu alanları korur |
| Pin | `agents/report_why_chain.py` | `pin_agent_why_chains_to_report` | Merge sonrası agent why_chain zorla yazılır |
| Başlık düzeltme | `agents/skillbased_docx_agent.py` | `_enforce_taxonomy_titles` | Dal/kök BARSEL başlıkları (zinciri değiştirmez) |
| **7. HTML/DOCX yazma** | `agents/skillbased_docx_agent.py` | `_build_branches`, `_html_branches` | 5-Why tablosu + kök neden kutusu |
| Kök neden bölümü | `agents/skillbased_docx_agent.py` | `_html_root_causes`, `_ensure_root_causes_from_branches` | Bölüm 6 nihai kök nedenler |
| Decision tree | `agents/decision_tree_mermaid.py` | `DecisionTreeGenerator` | `part3_rca` dallarından ağaç (W1: `build_event_why1_question`) |

### Yapılacaklar (P1.26)

| Görev | Durum | İş |
|-------|--------|-----|
| **R1** | ✅ | Merge sonrası `branches[].why_chain` → **agent/fallback'ten zorla pin** (`pin_agent_why_chains_to_report`) |
| **R2** | ✅ | `build_shared_event_question` — tüm dallarda aynı NEDEN 1 olay sorusu |
| **R3** | ✅ | `CONTENT_SYSTEM_PROMPT` şeması: NEDEN 1 = olay; "why_chain'i yeniden yazma" kuralı |
| **R4** | ✅ | Render öncesi `len(why_chain)==5` doğrulama / uyarı (`validate_report_why_chains`) |
| **R5** | ✅ | Agent W1/W2 klasik shift (`98940ca`); 4.1 tekrar kaldırıldı |

**Deploy:** Billing entegrasyonu gibi pin + 1M token kotası için **API + Celery worker** yeniden deploy gerekir.

**Kabul kriterleri:**
- Raporda her dal: ortak NEDEN 1 olay sorusu + kısa A/B cevap + 5 satır.
- `part3_rca.analysis_branches[].why_chain` ile HTML tablosu birebir örtüşmeli (LLM override yok).
- Kök neden kutusu `derive_root_cause_from_why5` + `enrich_root_cause_from_taxonomy` çıktısıyla uyumlu.

**Kod dokunuşu:** `agents/report_why_chain.py` (pin), `agents/skillbased_docx_agent.py` (wire + prompt), `agents/why_chain_quality.py` (shared event Q), `tests/test_report_why_chain.py`, `tests/test_why_chain_quality.py`.

**Sıra:** R1 → R2 → R3 → R4.

## P1.25 Etkileşimli form 504 — bootstrap + retry ✅

**Sorun:** Bazı kullanıcılar etkileşimli form gönderiminde `HTTP 504` alıyor (Railway cold-start, iki ayrı gateway çağrısı, Redis blokajı).

| İş | Durum | Detay |
|----|--------|-------|
| Tek bootstrap endpoint | ✅ | `POST /api/v1/incidents/bootstrap/interactive` — Part 1+2 tek çağrı (LLM yok) |
| Gateway retry | ✅ | `fetchGatewayWithRetry` — 502/503/504 için 4 deneme, 3.5s aralık |
| Cold-start prewarm | ✅ | Form sekmesi açılınca `checkHealth()` arka planda |
| Redis fast-fail | ✅ | `socket_connect_timeout=2`, `socket_timeout=2` |
| Async persist | ✅ | Fast path kayıtları `asyncio.to_thread` ile Redis'e yazılır |

**Kabul:** Etkileşimli analiz formu gönderimi çoğu cold-start senaryosunda 504 vermeden chat sekmesine geçmeli.

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

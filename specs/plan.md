# Product and Architecture Plan

## Product Goal

DeepWhy is an HSG245-based multi-agent Root Cause Analysis platform that combines:

- Structured incident intake,
- Interactive Human-in-the-Loop (HITL) questioning,
- DSPy-powered 5-Why root cause analysis,
- Action planning and report generation (PDF/DOCX/HTML),
- Multi-tenant API and async execution.

## Core User Flows

1. User submits incident form (Part 1 + Part 2 bootstrap).
   - User can attach extra photos/documents as incident evidence.
2. HITL questioning refines context with incident-specific prompts.
   - Entry UX should start with incident summary and an explicit analysis notice,
     not taxonomy-generic opening questions.
   - After initial immediate-cause extraction, deepening questions should be
     generated contextually from `agents/knowledge_base.py` and answered via selectable options.
   - **Answer modes (done):** `yes_no_unknown`, `free_text` (kaç/deneyim/miktar heuristics),
     `choice` chips; hybrid optional textarea under Yes/No; Enter or chip click advances to next question.
   - **Interactive bootstrap (done):** `POST /api/v1/incidents/{id}/assessment/form` saves Part 2 from
     form fields without Assessment Agent LLM, then opens chat tab immediately.
3. Async pipeline starts (Part 3 + Part 4).
4. User observes progress via WebSocket/polling.
5. User exports report artifacts (HTML/DOCX download; preview without mandatory popups).
6. *(Planned)* On report completion, system emails artifacts to the authenticated user's
   registered address (Kinde/profile email), with tenant-scoped secure links as fallback.

## Report Delivery UX

- **HTML oluştur** must not depend on `window.open('')` blank popups (blocked on cpanel and many
  corporate browsers). Primary path: generate artifacts server-side, then **trigger file download**
  via blob/anchor; optional preview opens HTML in a new tab from blob URL or falls back to download.
- **Part 3 readiness:** UI and API tolerate short delays between pipeline `completed` and
  `incident.part3` / `report_artifacts` persistence (retry before failing).
- **Email delivery (planned, P0.10):** after successful generation, worker sends one message to
  `owner_user_id` email with HTML (+ optional DOCX) attachments or signed download links;
  idempotent per `incident_id` + job id; opt-in preferences per tenant/user.
- **Raporlar (done — server + UI):** Mongo `rca.deepwhy_saved_items` per `tenant_id` + `owner_user_id`;
  tab lists reports/drafts, HTML + decision tree artifacts, Word download, rename-on-click titles,
  two-column layout (reports + sticky drafts sidebar). Email delivery still planned (P0.10).

## Evidence Attachment and Multimodal Context

- Incident intake should support file attachments (photos, PDFs, office docs, scans).
- Attached evidence should be processed and summarized into structured context for analysis:
  - OCR/text extraction from documents,
  - optional image captioning/object cues for photos,
  - metadata capture (filename, type, uploader, upload time, tenant scope).
- HITL and RCA prompts should consume attachment-derived evidence as supplemental context,
  while preserving explicit traceability to attachment sources.
- Evidence handling should respect security and compliance:
  - tenant-isolated storage paths,
  - file type and size validation,
  - malware/unsafe file screening policy,
  - retention/deletion controls aligned with tenant policy.

### Multimodal enrichment pipeline (target architecture)

User inputs feed a **three-layer** enrichment path before the existing RCA pipeline runs unchanged:

```
Kullanıcı Girdileri
├── Olay metni (mevcut)
├── Fotoğraflar (JPG/PNG)
├── Dökümanlar (PDF/DOCX)
└── Şirket profili (opsiyonel)
        ↓
[1. ÇIKARMA KATMANI]     — paralel, dosya tipine göre farklı extractor
        ↓
[2. BAĞLAM BİRLEŞTİRME]   — tek enriched_context bloğu
        ↓
[3. MEVCUT RCA PIPELINE] — RootCauseAgentV3_1 + rapor üretimi
        ↓
Şirkete özgün rapor
```

**Layer 1 — Extraction (per file type, parallel)**

| Kaynak | Yöntem | Structured çıktı (özet JSON, ham metin değil) |
|--------|--------|--------------------------------------------------|
| Fotoğraflar | Vision model (Claude / GPT-4o Vision) | `ekipman_tipi`, `kkd_durumu`, `loto_durumu`, `alan_koşulları`, `görsel_kanıtlar[]`, `anomaliler[]`, `güven_skoru` |
| PDF/DOCX | PyMuPDF / python-docx → LLM özet | `döküman_tipi`, `son_güncelleme_tarihi`, `ilgili_maddeler[]`, `eksik_imzalar[]`, `geçerlilik_durumu`, `güven_skoru` |
| Sertifikalar | OCR (Tesseract) veya Vision | isim, tarih, kapsam; olaydaki kişiyle eşleştirme |

Token budget (hedef): ~500 token/fotoğraf, ~800 token/döküman — çıkarma adımları **özet JSON** döndürür.

**Layer 2 — Context merge**

Tüm extractor çıktıları tek `enriched_context` metnine birleştirilir (bölümler: GÖRSEL KANIT, DÖKÜMAN KANIT, SERTİFİKA DURUMU, ŞİRKET PROFİLİ). Bu blok **mevcut `incident_summary` sonuna eklenir**; pipeline imzaları ve agent graph aynı kalır.

Düşük güven skorlu kanıtlar raporda “olası” olarak işaretlenir.

**Layer 3 — Company memory (oracle)**

Per-tenant şirket profili (MongoDB veya JSON), örnek alanlar:

- `şirket_id`, `geçmiş_kök_nedenler[]`, `tekrar_örüntüsü`, `sektör`, `ekipman_parkı[]`, `bilinen_riskler[]`

At runtime: `investigation_data["oracle_context"] = şirket_profili` (field already exists in codebase). Her tamamlanan rapor sonrası profil güncellenir (yeni kök neden kodu, tekrar sayacı).

**Data flow summary**

```
Fotoğraflar  → Vision API  → görsel_kanıtlar{}
PDF/DOCX     → OCR + LLM   → döküman_kanıtlar{}
Sertifikalar → OCR         → sertifika_durumu{}
Şirket DB    → sorgu       → şirket_profili{}
                    ↓
              enriched_context
                    ↓
         incident_summary'e ekle
                    ↓
         RootCauseAgentV3_1.analyze_root_causes()
                    ↓
         tenant-specific report
```

**Implementation constraints**

- Extraction jobs run with `asyncio.gather()`; RCA pipeline starts only after all extractions complete (or explicit partial-failure policy).
- Tenant + `owner_user_id` isolation for attachments and company profile stores (same cluster as `deepwhy_saved_items` / `rca`).
- **Current state:** manual form sends client-side text excerpts + file manifest in `how_happened` (P1.7 partial); server-side Layer 1–3 not yet implemented — see `specs/roadmap.md` **P1.13**.

## System Architecture

- Frontend: `admin_pan/Admin/src/rca-frontend/`
  - `RcaFrontendHub.jsx` controls form and interactive tabs.
  - `ChatInterface.jsx` handles HITL and live pipeline flow.
- API: `api/main.py`
  - Multi-tenant request resolution,
  - Incident lifecycle endpoints,
  - HITL question endpoint,
  - Job status + websocket endpoint.
- Worker: `tasks/pipeline_tasks.py` + `celery_app.py`
  - Executes root cause and action plan stages asynchronously.
  - Runtime scaling strategy (Railway):
    - Default `prefork` pool with Celery autoscale.
    - Scale range: min 1, max 5 worker processes per container.
    - Goal: avoid always-on high concurrency while handling burst traffic.
  - Burst scaling acceptance (P0.5 baseline):
    - Idle worker must run at min process count.
    - Under queue pressure worker must scale up to configured max.
    - Scale-down must occur automatically after queue drains.
  - Reliability hardening requirements:
    - Heartbeat/visibility-timeout tuning for long RCA tasks,
    - Reduced CPU-blocking critical sections,
    - 3–5 concurrent analysis stability without task loss.
- Agents: `agents/`
  - `rootcause_agent_v3_1.py` as primary RCA engine,
  - `rootcause_agent_v2.py` fallback,
  - `branch_critic.py`, `actionplan_agent.py`, reporting agents.
- Shared services: `shared/`
  - Tenant store/auth, hybrid cache, oracle context.

## Non-Functional Requirements

- Tenant isolation for incidents/jobs/cache keys.
- Fail-safe fallback from V3.1 to V2 for root cause engine.
- Build/deploy resilience on Railway:
  - slim `Dockerfile` image for API/worker (avoids cold-build disk exhaustion),
  - production image must include `hitl_test/` (HITL question service imports at runtime).
- Deterministic operational visibility for worker/job status.
- Action Plan JSON must be schema-valid or recoverable via retry/sanitizer path
  (markdown-fence/trailing-comma tolerant pre-parser).
- Worker stability for long RCA runs must include:
  - heartbeat-safe broker settings (`visibility_timeout`, `prefetch=1` for long tasks),
  - explicit handling/monitoring of heartbeat drift and missed-heartbeat warnings,
  - infrastructure-level clock synchronization (NTP) and non-root runtime policy.

## ABS-Guided Learning and Retrieval Strategy

- Use `knowlodge_base/ABSG_Consulting_Inc_Root_Cause_Map_Guidance_Document_1703.pdf`
  as the primary methodology reference for:
  - Causal-factor-first analysis,
  - Why-tree expansion before coding,
  - Multi-root-cause treatment and recommendation depth.
- Synthetic DSPy data generation must stay aligned with ABS guidance:
  - Build incident variants from causal factors and management system gaps,
  - Avoid generic endpoint labels ("human error", "training lack") unless supported by chain evidence,
  - Preserve explicit traceability from Why steps to final root-cause statements.
- HITL deepening must follow form-safe behavior:
  - Ask targeted deep-dive questions per emerging root-cause branch,
  - Do not re-ask fields already captured in incident form data,
  - Request additional evidence (timeline, procedure, supervision, maintenance, barrier status)
    only when needed to disambiguate competing root-cause paths.
- RAG must be optional but production-ready:
  - Retrieve ABS/taxonomy context to guide question generation and root-cause coding,
  - Keep tenant-scoped retrieval boundaries,
  - Keep deterministic fallback path when retrieval is unavailable.
  - Keep normalized HGS taxonomy records in Mongo for code-level retrieval/question generation
    (target: `hgs_taxonomy.taxonomy_items`).

## UX and Report Consistency Requirements

- Report artifacts must honor user-selected language end-to-end:
  - investigation/output language selected in frontend should propagate to report generation,
  - static report shell labels (DOCX/HTML headings) must not stay Turkish when another language is selected.
- Visual consistency target:
  - report output theme should align with admin panel primary/secondary palette.
- Interactive entry behavior:
  - switching to interactive analysis should open chat-first experience immediately
    (fast `assessment/form` path; no blocking on four Assessment Agent LLM calls).
- HITL answer collection:
  - questions that need quantities or narrative use `free_text` (not Yes/No only);
  - binary questions may show Yes/No/Unknown plus optional written answer;
  - single-choice chips and Enter submit auto-advance to the next question.
- Pipeline transparency:
  - while root cause and report stages run, users should see continuously streaming progress
    and Why-chain lines to reduce waiting friction.

## Smart Hybrid RCA (Planned — P1.14)

Branch count and labels are **suggested from incident severity**, then **confirmed by the user** (Option C — recommended hybrid):

- Fatal / serious harm → default **3 branches** with guidance copy (*at least 3 branches recommended*).
- Minor injury → **2 branches**; near-miss → **1 branch**.
- Default templates: Human/Behavior, Supervision/Organization, System/Procedure — user may accept, rename, or rewrite.
- `+ Add branch` always visible; **cannot add** while an existing branch is empty (*fill current branch first*).
- **Minimum one mandatory branch**; MVP may disallow deletion below minimum while allowing adds (quality floor for new users).
- On report completion: per-branch completeness score; block approval if required branches are incomplete.
- Approved branch structure feeds HITL why-probe paths and Part 3 / decision tree generation.

MVP implementation: severity → branch-count lookup table in frontend + API persistence on incident/draft; tenant-configurable thresholds later.

## User Token Quota (Planned — P1.15)

Per-user token account scoped by `tenant_id` + `owner_user_id` (Kinde):

- **Balance** decremented on billable operations (pipeline, HITL LLM, full assessment, report generation).
- **Ledger** records each debit/credit with idempotency keys tied to `job_id` / request id.
- **Enforcement** at API (and optionally worker pre-flight): insufficient balance returns explicit error; UI disables new analysis/report actions.
- **Pricing alignment:** tier definitions in P0.11 map to monthly token budgets and per-report credit costs.
- **UX:** remaining balance indicator; warnings at 80%/95%; hard stop at zero while preserving read access to saved reports.

Storage target: Mongo (`user_token_accounts`, `token_ledger` in `MONGODB_DB` / `rca`); in-memory fallback for local dev. Implemented: `shared/token_account.py`, usage API routes, Dashboard wiring, DeepWhy enforcement strip.

Env: `TOKEN_PERIOD_LIMIT`, `TOKEN_DEFAULT_BALANCE`, `TOKEN_ENFORCEMENT`, `TOKEN_*_ESTIMATE` per operation.

## Pricing Page Refresh Requirements

- Pricing page should be refreshed with a 3-tier card layout matching the target design language
  (dark background, highlighted middle plan, compact feature bullets).
- Tiers and monthly anchor prices:
  - Starter: `$29/ay`
  - Professional: `$99/ay` (badge: "En popüler")
  - Enterprise: `$299/ay`
- Each tier must include clear capacity and capability limits (report quota, **token/analysis credit budget**,
  analysis method scope, output formats, user seats, support/SLA level, API/SSO availability where applicable).
- Tier footer labels should communicate target segment:
  - Starter: KOBİ / bireysel HSE
  - Professional: Orta ölçekli işletme
  - Enterprise: Büyük sanayi / holding
- CTA and billing text should remain editable/configurable (future campaign/discount support).
- Pricing content should be locale-aware (TR now, EN-ready i18n keys for later switch).

## Report Productization Requirements

- Completion notification:
  - automatic email to the account email used at login (Kinde),
  - attach generated HTML (and DOCX when available) or time-limited signed URLs,
  - success/failure templates; delivery audit log (see `specs/roadmap.md` P0.10).
- Cover page personalization:
  - first page should be user-editable with alternative templates (e.g. formal, executive, minimal).
  - user should be able to switch template variant before export.
- DOCX and HTML structural parity:
  - section hierarchy/order should remain aligned between Word and HTML versions.
  - HSG/technical code clutter should be removable from user-facing report body.
  - final code-removal policy should be confirmed with Baris Bey before production lock.
- Branding controls:
  - optional logo upload/selection per tenant and per report.
  - logo should be placeable in cover/header/footer zones based on template.
- Document authenticity/protection:
  - support configurable watermark/hologram overlay in output artifacts.
  - watermark/hologram should support draft/final modes and tenant-level defaults.

## Critical RCA Quality Gaps (DSPy/V3.1)

- SemanticVerifier is currently too coarse for 5-Why semantic duplicate detection:
  - token-overlap/Jaccard style checks overcount shared domain terms (`production`, `LOTO`, etc.),
  - fixed threshold behavior is not domain-calibrated,
  - this can trigger false diversity alarms or miss real paraphrase duplication.
- BranchCritic timing is late in the flow:
  - critic runs after all branches are generated,
  - branch 3/4 generation does not proactively avoid branch 1/2 reasoning overlap,
  - regenerated branches are not consistently revalidated for chain-level coherence.
- `chain_quality` signal is not yet trustworthy:
  - score path behaves like a near-constant high value,
  - Why-to-Why deepening quality and paraphrase loops are not measured robustly.
- MIPROv2 optimization is not yet applied to Why signatures:
  - prompts/signatures run mostly with manual definitions,
  - few-shot optimization path is limited,
  - model tends to generic patterns under ambiguity.

## RCA Improvement Priority (Ordered)

- Immediate:
  - adopt MIPROv2-based optimization for Why signatures,
  - replace placeholder chain-quality scoring with measurable chain metrics,
  - move SemanticVerifier to embedding-based cosine similarity (or weighted TF-IDF fallback).
- Mid-term:
  - shift BranchCritic to earlier branch-generation stages,
  - enforce post-regeneration coherence checks,
  - inject per-branch diversity constraints before branch generation.
- Later:
  - introduce DSPy Assertions for rule-based constraints,
  - add automatic few-shot retrieval/selection support (RAG-assisted),
  - add reverse consistency checks (Why-5 back to Why-1 chain logic).

## Spec Ownership

- Product + flow details: `README.md`
- Execution backlog: `specs/roadmap.md`
- Stack and runtime constraints: `specs/tech-stack.md`

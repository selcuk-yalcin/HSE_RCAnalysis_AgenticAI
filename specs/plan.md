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
3. Async pipeline starts (Part 3 + Part 4).
4. User observes progress via WebSocket/polling.
5. User exports report artifacts.

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
- Build/deploy resilience on Railway.
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
  - switching to interactive analysis should open chat-first experience immediately.
- Pipeline transparency:
  - while root cause and report stages run, users should see continuously streaming progress
    and Why-chain lines to reduce waiting friction.

## Pricing Page Refresh Requirements

- Pricing page should be refreshed with a 3-tier card layout matching the target design language
  (dark background, highlighted middle plan, compact feature bullets).
- Tiers and monthly anchor prices:
  - Starter: `$29/ay`
  - Professional: `$99/ay` (badge: "En popüler")
  - Enterprise: `$299/ay`
- Each tier must include clear capacity and capability limits (report quota, analysis method scope,
  output formats, user seats, support/SLA level, API/SSO availability where applicable).
- Tier footer labels should communicate target segment:
  - Starter: KOBİ / bireysel HSE
  - Professional: Orta ölçekli işletme
  - Enterprise: Büyük sanayi / holding
- CTA and billing text should remain editable/configurable (future campaign/discount support).
- Pricing content should be locale-aware (TR now, EN-ready i18n keys for later switch).

## Report Productization Requirements

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

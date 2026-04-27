# Execution Roadmap

Source: synchronized from root `TODO.md`.

## P0 (Critical)

### P0.1 Multi-Tenant User Management

- Persistent tenant/user registry in Redis.
- Admin tenant and user management APIs.
- Role-based authorization on pipeline and incident operations.
- Frontend tenant header propagation.

### P0.2 5-Step Incident-Specific HITL

- Add LLM-driven incident-specific HITL question generator.
- Remove generic first-step prompts; start with incident summary + analysis notice.
- After first immediate-cause stage, generate deeper selectable questions from `agents/knowledge_base.py`.
- Fallback from static logic to LLM by quality threshold.
- Improve Why-chain continuity and answer handling options.
- Persist HITL logs for training reuse.
- Keep a single primary large-area frontend analysis flow (remove duplicated secondary Why widgets).
- ✅ Show initial immediate causes without taxonomy codes in chat intro, then switch directly to deep-dive collaboration prompts. (DONE)
- ✅ Filter out generic/duplicative HITL questions already covered by manual form fields (timeline/training/PPE/weather/lighting). (DONE)
- ✅ Generate Why-probe questions from taxonomy code semantics (choose-if/not-this-if) before generic gap questions. (DONE - taxonomy-first probe)

### P0.3 Frontend Live Streaming

- Branch/why-level granular progress callbacks.
- Enriched job payload fields for UI.
- Live timeline component in chat UI.
- WebSocket reconnect and robust failure UX.

### P0.4 Worker OpenRouter 401 Stabilization

- Eliminate `Missing Authentication header` failures in Step 3 (Celery worker).
- Enforce deploy/runtime parity between API and worker services.
- Add deterministic startup diagnostics for auth/debug visibility.
- Verify worker is running latest commit via build fingerprint and deploy metadata.
- Add clear runbook for Railway redeploy + env parity checks.
- Acceptance:
  - Worker logs show build fingerprint and OpenRouter runtime config on startup.
  - HITL flow reaches Part 3+Part 4 completion without OpenRouter 401.
  - Same env/config behavior is reproducible after restart and redeploy.

### P0.5 Worker Burst Scaling Without Always-On High Load

- Configure Celery worker autoscaling for burst traffic.
- Default runtime profile:
  - `CELERY_POOL=prefork`
  - `CELERY_AUTOSCALE_MAX=5`
  - `CELERY_AUTOSCALE_MIN=1`
- Keep baseline resource usage low while allowing temporary parallel RCA jobs.
- Acceptance:
  - Idle worker runs at min process count.
  - Under queue pressure worker scales up to configured max.
  - Scale-down occurs automatically after queue drains.

### P0.6 Action Plan JSON Robustness

- ✅ Enforce stricter Action Plan JSON schema validation. (DONE - schema gate in `ActionPlanAgent`)
- ✅ Add retry and \"json-only\" sanitizer parser for malformed outputs. (DONE - 3-attempt regeneration + sanitize candidates)
- ✅ Sanitize markdown fences and trailing commas before parsing. (DONE - candidate sanitizer in `ActionPlanAgent`)
- ✅ Add parse telemetry and malformed-output regression tests. (DONE - telemetry logs + `tests/test_actionplan_json_hardening.py`)

### P0.7 Celery Long-Run Reliability

- ✅ Keep `prefork + autoscale` as baseline worker runtime. (DONE)
- ✅ Tune heartbeat and broker visibility timeout for long RCA tasks. (DONE - env-driven visibility timeout + health interval + prefetch=1)
- ✅ Reduce single-worker CPU blocking with staged checkpoints. (DONE - cooperative progress checkpoints in `tasks/pipeline_tasks.py`)
- ✅ Add 3-5 parallel-run reliability/load validation and ops visibility. (DONE - ops summary in `shared/ops_celery.py` + `tests/test_parallel_rca_load_scenario.py`)

### P0.8 Multilingual Report + Interactive UX Stream

- ✅ Propagate selected frontend language to investigate/report pipeline (`output_language`). (DONE)
- ✅ Ensure report shell labels (DOCX + HTML) follow selected language (minimum: non-TR must not render Turkish headers). (DONE - baseline)
- ✅ Align report visual palette with admin panel theme tokens. (DONE)
- ✅ Interactive analysis must open chat-first and show active chatbot surface immediately. (DONE)
- ✅ Stream live root-cause/progress lines in Agent Pipeline area during analysis/report generation. (DONE)

### P0.9 Report Template, Branding, and Hologram

- Add editable and alternative cover-page templates for report generation.
- Keep DOCX and HTML report structures aligned section-by-section.
- Add user-facing option to hide/remove technical code identifiers from report body.
- Confirm final code-visibility policy with Baris Bey before release.
- Add optional logo insertion support (tenant-level default + per-report override).
- Add watermark/hologram support for draft/final report modes.

### P1.7 Evidence Attachments in Analysis Flow

- Add incident-level file upload support (photo + document evidence).
- Add backend attachment ingestion pipeline (validation, storage, metadata indexing).
- Extract attachment context (OCR/text and image cues) for RCA/HITL prompt augmentation.
- Show attachment-derived evidence summary in interactive analysis view.
- Keep tenant-isolated attachment storage and configurable retention policy.

## P1 (Near-Term)

### P1.1 Synthetic Data Pipeline

- ✅ Mongo output mode for synthetic generation. (DONE - `--store mongo|both` + dataset/example persistence)
- Tenant partitioning and seeded generation from incidents.
- Scheduled generation jobs and admin trigger endpoint.

### P1.2 DSPy MIPROv2 Integration

- ✅ Define RCA quality metrics. (DONE - `agents/training/dspy_metrics.py`)
- ✅ Build optimize/compile pipeline for WhyChain. (DONE - `agents/training/optimize_rca.py`, WhyChain input adaptation + MIPRO run path)
- ✅ Version compiled artifacts and support runtime loading. (DONE - versioned summary artifacts in `agents/training/compiled/`)
- Add baseline vs compiled A/B evaluation.

### P1.3 Operational Training Workflow

- Standardize train/eval/promote commands.
- Store run artifacts and lineage metadata.
- Nightly CI training with release gate.

### P1.4 Tenant Insights

- Time trends, severity and category distributions.
- Department/location analytics breakdown.
- Dashboard visualization in admin panel.

### P1.5 RAG Rollout

- Managed embeddings and vector store.
- Tenant-isolated vector namespaces.
- Controlled RAG prompt injection strategy.
- Add normalized HGS taxonomy store in Mongo (`hgs_taxonomy.taxonomy_items`) for taxonomy-aware retrieval/questioning.

### P1.6 ABS-Guided DSPy Training + Deep HITL

- Extend `agents/synetic_data_preperation/hse_synthetic_data.py` to produce
  ABS-aligned Why chains (causal-factor-first, management-system-gap-aware).
- Build training/eval set variants from ABS style patterns:
  - multiple plausible root causes per causal factor,
  - evidence-based questioning and recommendation linkage.
- Add HITL deep-question policy:
  - ask branch-specific disambiguation questions at each Why depth,
  - skip data already present in form payload,
  - enforce evidence collection prompts for timeline/procedure/maintenance/supervision.
- Integrate RAG into root-cause and HITL phases with controlled retrieval:
  - query only relevant ABS/taxonomy chunks,
  - inject concise citations into prompts,
  - keep fallback to non-RAG prompts when confidence is low.
- Railway vector DB decision:
  - primary: MongoDB Atlas Vector Search (tenant namespace, managed ops),
  - avoid local file-based FAISS/Chroma persistence in production workers.

### P1.8 Ordered Delivery Plan (Synthetic -> DB -> RAG -> MIPROv2)

- ✅ Step 1: ABS-guided synthetic dataset generation and quality gate. (DONE - profile + stricter quality gate)
- ✅ Step 2: Dataset versioning and persistence into database (tenant + dataset lineage). (DONE - dataset metadata + Mongo store mode)
- ✅ Step 3: ABS guidance PDF chunking and vector DB indexing for RAG retrieval. (DONE - `build_abs_guidance_vector_store.py`)
- ✅ Step 4: MIPROv2 optimization using curated dataset versions (+ baseline vs optimized eval). (DONE - `agents/training/optimize_rca.py`, `agents/training/dspy_metrics.py`)
- ✅ Step 5: Production promotion with rollback-safe model/version controls. (DONE - `agents/training/promote_model.py`)

### P1.9 Model Strategy by Stage

- Training/synthetic generation profile:
  - prefer `google/gemini-2.5-flash` for speed and cost efficiency.
- Agentic RCA + report generation profile:
  - prefer `anthropic/claude-sonnet-4.5` for depth, consistency, and report quality.
- Runtime fallback policy:
  - primary model failure should degrade gracefully to secondary profile.

## P2 (Mid-Term)

### P2.1 Voice Input

- Incident voice capture and STT integration.

### P2.2 Language Strategy

- Output language consistency and broader locale support.

### P2.3 Test Coverage

- Unit tests for tenant/cache/HITL services.
- CI mocking for LLM interfaces.
- Playwright e2e flow validation.

### P2.4 Observability

- Structured logging, latency/token metrics, Sentry/Highlight.

## Continuous

- Bump worker build fingerprint every release.
- Maintain key rotation playbook.
- Archive legacy agent versions.
- Exclude generated outputs from git tracking.

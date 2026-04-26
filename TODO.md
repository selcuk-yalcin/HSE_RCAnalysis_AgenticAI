# TODO — DeepWhy / HSE RCA AgenticAI

Roadmap format for each item: **goal → current state → tasks → acceptance criteria → related files**.

Priority: P0 (critical) → P1 (near-term) → P2 (mid-term).

---

## P0.1 — Multi-Tenant User Management

**Goal**: Isolated user, role, and API key management for each company (tenant), with
tenant creation and user invitation from the admin panel.

**Current state**:
- `shared/tenant_store.py`, `shared/tenant_auth.py`, `shared/hybrid_cache.py`, and
  Redis incident keys are tenant-isolated (READY).
- Tenant resolution uses `X-Tenant-ID` header or `TENANT_API_KEYS_JSON`.
- No persistent user table yet.
- Frontend uses Kinde authentication, but tenant context is not consistently sent to backend headers.

**Tasks**:
- [ ] Add `shared/tenant_registry.py` with Mongo collections `tenants` and `tenant_users`.
  - `tenants`: `{tenant_id, slug, name, plan, created_at, settings}`
  - `tenant_users`: `{tenant_id, kinde_user_id, email, role(admin|analyst|viewer), api_keys[]}`
- [ ] Add routes in `api/main.py`:
  - `/api/v1/admin/tenants` (CRUD)
  - `/api/v1/admin/tenants/{id}/users` (invite/list/update role)
- [ ] Extend `shared/tenant_auth.py` to resolve `tenant_id` and `role` from Kinde JWT.
- [ ] Add a \"Workspace\" page to admin panel for tenant creation and user invites.
- [ ] Add role-based guards to `_jobs` / `_incidents` paths (e.g. viewer cannot start pipeline).
- [ ] Auto-inject `X-Tenant-ID` from frontend (`hsg245Api.js` + Vercel proxy).

**Acceptance criteria**:
- Two tenants can run the same incident IDs concurrently without collisions.
- `viewer` role receives 403 on `pipeline/start`.
- Tenant deletion also clears Redis + Mongo cache data.

**Related files**: `shared/tenant_*.py`, `api/main.py`, `admin_pan/Admin/src/`.

---

## P0.2 — 5-Step Incident-Specific HITL Flow

**Goal**: After manual form submission, run interactive HITL with incident-specific
questions and increasing depth at each Why level.

**Current state**:
- `agents/hitl_question_service.py` supports `next_hitl_questions` + `next_why_probe_questions`.
- Frontend `ChatInterface.jsx` runs code-based branches from why level 1 to 5.
- Questions currently come from disambiguation bank + taxonomy gap logic; no LLM-based
  incident-specific question generation yet.
- Answers are passed to Part 3 as `why_probe_answers`.

**Tasks**:
- [ ] Remove generic opening questions in HITL start.
  - First card must show incident summary and a clear note:
    - \"Analizi tamamlamak icin olayla ilgili sorular soracagiz.\"
- [ ] Add LLM-based incident-specific question generator using incident summary +
  immediate code via `dspy.Predict` (new module: `agents/hitl_dynamic_llm.py`).
- [ ] After first immediate-cause extraction, generate deeper follow-up questions from
  `agents/knowledge_base.py` (incident + immediate/root cause context aware).
- [ ] Force question type to selectable options (multi-choice style) so answers are
  machine-consumable for deterministic RCA depth increase.
- [ ] Add fallback to LLM in `hitl_question_service` when quality score is below threshold.
- [ ] Inject previous answer keywords into next Why question for chain continuity.
- [ ] Add per-Why-level progress indicator (5-step) in frontend.
- [ ] Add \"skip\" / \"I don't know\" options and define RCA handling behavior.
- [ ] Persist HITL logs per tenant in Mongo for training data.
- [ ] Remove duplicated/secondary Why chain widgets from frontend; keep a single primary
  large-area live flow panel for analysis progression.

**Acceptance criteria**:
- Across 5 scenario categories (fall, electric, chemical, crush, train odor), HITL
  generates at least 3 incident-specific questions and filters generic questions.
- HITL answers are referenced directly in Part 3 RCA chains.
- The first HITL screen never starts with taxonomy-generic prompts; it starts with
  incident summary + analysis notice and then incident-specific selectable questions.
- RCA branch depth and root-cause diversity improve across repeated runs of the same
  incident family (less \"same root cause every time\" behavior).

**Related files**:
- `agents/hitl_question_service.py`
- `agents/hitl_disambiguation_bank.py`
- `hitl_test/question_engine.py`
- `admin_pan/Admin/src/rca-frontend/components/ChatInterface.jsx`

---

## P0.3 — Frontend Streaming (Live Pipeline)

**Goal**: After `pipeline/start`, users can see in real time which Why branch is running
and which C/D code is being produced.

**Current state**:
- `api/main.py` already provides `/ws/jobs/{job_id}` and basic stage/progress updates.
- `tasks/pipeline_tasks.py` emits only coarse stages (`investigate`, `actionplan`).
- Frontend tries WebSocket via `runPipelineJobWithPolling`, then falls back to polling.

**Tasks**:
- [ ] Add progress callback in `RootCauseAgentV3_1` (`on_progress(stage, branch, why_level, message)`).
- [ ] Forward callback events from `tasks/pipeline_tasks.py` via `update_state` or Redis pub/sub.
- [ ] Extend `_normalize_celery_job` fields (`current_branch`, `current_why_level`, `latest_message`).
- [ ] Add a live timeline component in chat (`PipelineLiveTimeline.jsx`).
- [ ] Add explicit \"pipeline failed\" UI for terminal errors.
- [ ] Add WebSocket auto-reconnect with backoff.

**Acceptance criteria**:
- User can follow all 25 analysis steps (5 branches × 5 Why) in order.
- On temporary network loss, WebSocket reconnects and resumes the same job.

**Related files**:
- `agents/rootcause_agent_v3_1.py`
- `tasks/pipeline_tasks.py`
- `api/main.py`
- `admin_pan/Admin/src/services/hsg245Api.js`
- `admin_pan/Admin/src/rca-frontend/components/ChatInterface.jsx`

---

## P0.4 — Railway Worker Replica Autoscaling (1..5 On-Demand)

**Goal**: Prevent long queue waits by scaling worker capacity between 1 and 5 replicas
only when needed, while keeping idle cost low.

**Current state**:
- Celery process autoscaling is configured in worker runtime (`prefork`, autoscale min/max).
- Replica scaling policy is still mostly manual from Railway UI.

**Tasks**:
- [ ] Add Railway service scaling profile for worker:
  - idle baseline: `replicas=1`
  - burst profile: `replicas=2..5`
- [ ] Define queue-based trigger policy:
  - if queued jobs > N for T seconds, increase replicas by 1 (max 5)
  - if queue is empty for cooldown window, decrease replicas by 1 (min 1)
- [ ] Document operational toggles in runbook (`CELERY_AUTOSCALE_MIN/MAX`, replica override).
- [ ] Add ops endpoint/metric that reports current queue depth + active workers.
- [ ] Validate no starvation between interactive and batch analysis (optional queue split if needed).

**Acceptance criteria**:
- Under low traffic, worker remains at 1 replica.
- Under burst traffic, replicas scale up to max 5 without manual intervention.
- After burst ends, replicas return to 1 automatically.
- Median wait time from `queued` to `running` improves for concurrent runs.

**Related files**:
- `scripts/railway_celery_worker.sh`
- `tasks/pipeline_tasks.py`
- `api/main.py`
- `shared/ops_celery.py`

---

## P0.5 — Action Plan JSON Robustness and Parser Hardening

**Goal**: Prevent malformed LLM JSON from degrading Part 4 quality and reduce fallback-only plans.

**Current state**:
- Action plan generation occasionally returns malformed JSON (comma/fence issues), then falls back.
- Logs show parse errors in production, especially under long/complex outputs.

**Tasks**:
- [ ] Add strict Action Plan JSON schema validation before acceptance.
- [ ] Add retry strategy for malformed JSON responses (schema-guided regeneration).
- [ ] Add \"json-only\" sanitizer/parser:
  - strip markdown fences,
  - sanitize trailing commas,
  - extract first valid JSON object safely.
- [ ] Add parser telemetry fields (`parse_attempts`, `sanitized`, `fallback_reason`) to logs.
- [ ] Add tests for malformed outputs (missing comma, fence wrapper, truncated object).

**Acceptance criteria**:
- >=95% of action-plan responses parse without fallback on staging regression set.
- Fallback path remains available, but parse failures are explicitly classified and logged.

**Related files**:
- `agents/actionplan_agent.py`
- `tasks/pipeline_tasks.py`
- `tests/`

---

## P0.6 — Celery Reliability Under Long RCA Runs

**Goal**: Reduce heartbeat drift warnings and stabilize long-running concurrent RCA processing.

**Current state**:
- Worker uses `prefork` + autoscale but still shows heartbeat drift/missed heartbeat warnings under load.
- Long single-task CPU pressure can delay worker bookkeeping.

**Tasks**:
- [ ] Keep `prefork` + autoscale runtime defaults (`min=1`, `max=5`) and document per-env overrides.
- [ ] Tune Celery heartbeat-related settings and broker visibility timeout for long tasks.
- [ ] Split/limit CPU-heavy sections or add cooperative checkpoints to avoid single-process blocking.
- [ ] Add queue-depth + worker-heartbeat health surface in ops endpoint.
- [ ] Add load test scenario for 3-5 parallel RCA runs with acceptable queue wait and no task loss.

**Acceptance criteria**:
- No task loss/duplication in 3-5 parallel RCA runs.
- Heartbeat drift warnings are significantly reduced and monitored with clear thresholds.
- Queue latency remains within defined SLO during burst load.

**Related files**:
- `celery_app.py`
- `scripts/railway_celery_worker.sh`
- `tasks/pipeline_tasks.py`
- `shared/ops_celery.py`

---

## P1.1 — Synthetic Data Generation Pipeline (Internal)

**Goal**: Generate realistic synthetic data to optimize HSE 5-Why trainsets with DSPy MIPROv2.

**Current state**:
- `agents/synetic_data_preperation/hse_synthetic_data.py` is available as standalone CLI.
  - `--mode mock`: template-only, no API calls
  - `--mode real`: DSPy + OpenRouter
- Outputs: `hse_5why_train.jsonl` + `hse_dspy_trainset.json`.
- `load_dspy_examples` exists and is compatible with MIPRO input.
- Not integrated into production pipeline yet.

**Tasks**:
- [ ] Add Mongo output mode to CLI (`--store mongo --collection hse_5why_train`).
- [ ] Partition synthetic data by tenant: `data/synthetic/{tenant_id}/`.
- [ ] Move quality threshold to env (`SYN_DATA_QUALITY_THRESHOLD`).
- [ ] Add `--seed-from-incidents` mode (derive realistic variants from tenant incidents).
- [ ] Support tenant-level negative-example ratio.
- [ ] Add scheduled generation via cron / Celery beat.
- [ ] Add admin trigger endpoint: `/api/v1/admin/synthetic/generate`.

**Acceptance criteria**:
- Single command produces >=1000 high-quality examples (score > 0.7).
- Mongo stores versioned datasets (`dataset_id`, `created_at`, `n_examples`).

**Related files**: `agents/synetic_data_preperation/`.

---

## P1.2 — DSPy MIPROv2 Integration (Meta-Learning)

**Goal**: Optimize 5-Why prompts with MIPROv2 using metric-driven automation.

**Current state**:
- DSPy LM works in `agents/rootcause_agent_v3_1.py`.
- No formal `dspy.MIPROv2` or `BootstrapFewShot` optimization pipeline yet.
- `WhyChain`, `MetaRootCauseSynthesizer`, and `BranchCriticAgent` are modular and
  suitable for compile/optimization.

**Tasks**:
- [ ] Add `agents/training/dspy_metrics.py` with:
  - `chain_continuity_score`
  - `generic_pattern_penalty`
  - `system_level_root_cause_bonus`
  - weighted composite metric `hse_5why_metric`
- [ ] Add `agents/training/optimize_rca.py`:
  - `trainset = load_dspy_examples("hse_5why_train.jsonl")`
  - `devset` split
  - `optimizer = dspy.MIPROv2(metric=hse_5why_metric, auto="medium")`
  - `compiled = optimizer.compile(WhyChain(), trainset=trainset, valset=devset)`
- [ ] Version compiled artifacts under `agents/training/compiled/why_chain_v{N}.json`.
- [ ] Load latest compiled WhyChain in `RootCauseAgentV3_1` using `WHYCHAIN_COMPILED_PATH`.
- [ ] Add baseline vs compiled A/B report on dev set.
- [ ] Add continuous improvement loop using HITL-approved production samples.

**Acceptance criteria**:
- Compiled WhyChain improves dev metric by >=15% over baseline.
- Production worker loads compiled artifact with cold start under 5s.

**Related files**:
- new `agents/training/`
- `agents/rootcause_agent_v3_1.py`
- `agents/synetic_data_preperation/`

---

## P1.3 — Operational Training Workflow

**Goal**: Make synthetic + real data training/eval/release runnable through a single
operational flow.

**Current state**:
- Manual process: generate synthetic data → run MIPRO compile → deploy manually.

**Tasks**:
- [ ] Add `Makefile` or `scripts/train_pipeline.py`:
  ```
  make train-data
  make train-eval
  make train-promote VERSION=Nm
  ```
- [ ] Add run artifacts in `runs/` (`log`, `metric.json`, `artifact.json`).
- [ ] Add GitHub Actions nightly training with manual release approval.
- [ ] Add automatic inclusion of HITL-approved (`thumb_up`) samples from `feedback`.
- [ ] Track lineage: `dataset_version` → `compiled_version`.

**Acceptance criteria**:
- New model version can be promoted to production with one command after approval.
- Training run history is fully traceable.

**Related files**: new `scripts/`, `Makefile`, `.github/workflows/`.

---

## P1.4 — Pattern Analyzer and Tenant Insights

**Goal**: Provide per-tenant root cause trends, frequent codes, and period-based insights.

**Current state**:
- `agents/pattern_analyzer.py` exposes basic counters (`top_codes`, `status`).
- `/api/v1/analytics/patterns` endpoint exists.

**Tasks**:
- [ ] Add time trends (weekly/monthly) + severity breakdown.
- [ ] Add HSG245 category distribution (A/B/C/D).
- [ ] Add department and location breakdown.
- [ ] Add frontend insights dashboard (Recharts).

---

## P1.5 — RAG Pipeline Production Rollout

**Goal**: Make optional RAG analyzer in V3.1 production-ready (`ROOTCAUSE_USE_RAG=0` by default).

**Current state**:
- `agents/v3_vector_search/` and `rag_pipeline/` exist but are currently disabled
  due to build/runtime cost on Railway.
- Heavy deps (`sentence-transformers`, `faiss-cpu`) were removed from `requirements.txt`.

**Tasks**:
- [ ] Use managed embedding APIs (OpenRouter/OpenAI) instead of local heavy models.
- [ ] Use managed vector store (MongoDB Atlas Vector or Pinecone).
- [ ] Feed RAG context into WhyChain prompts.
- [ ] Isolate vector namespaces per tenant.

---

## P2.1 — Voice / Audio Input

**Goal**: Let users submit incident reports via voice dictation.

**Current state**: Not implemented.

**Tasks**:
- [ ] Add `MediaRecorder` UI to `IncidentForm`.
- [ ] Integrate Whisper / OpenRouter STT.
- [ ] Auto-fill transcript into `incidentDescription`.

---

## P2.2 — Language Strategy

**Goal**: Support languages beyond TR/EN with consistent UI + model output behavior.

**Current state**:
- Frontend translations currently cover TR/EN.
- Model output language is not consistently enforced.

**Tasks**:
- [ ] Bind model output language to selected form language.
- [ ] Plan and implement additional languages (DE, AR, FR).

---

## P2.3 — Test Coverage

**Current state**: Integration tests exist; unit and e2e coverage should be expanded.

**Tasks**:
- [ ] Add `pytest` unit tests for tenant store, hybrid cache, and HITL question service.
- [ ] Add OpenRouter mocking fixtures in CI (vcrpy/responses).
- [ ] Add Playwright e2e for form → HITL → pipeline → PDF flow.

---

## P2.4 — Observability

**Current state**:
- `shared/ops_celery.py` provides minimal inspect snapshot; no full observability stack.
- Worker startup build fingerprint is available in logs.

**Tasks**:
- [ ] Add structured JSON logs (loguru/structlog).
- [ ] Add OpenRouter latency/token metrics in health/ops endpoints.
- [ ] Add Sentry/Highlight integration.

---

## Continuous

- [ ] Bump worker build fingerprint each release (`celery_app.WORKER_BUILD_TAG`).
- [ ] Maintain OpenRouter key rotation playbook.
- [ ] Move legacy files in `agents/versiyonlar /` to `archive/` or remove.
- [ ] Add generated `outputs/` artifacts to `.gitignore`.

# HSE Root Cause Analysis — DeepWhy Agentic AI

An HSG245-based multi-agent Root Cause Analysis platform. It includes a DSPy-driven
5-Why chain, Human-in-the-Loop (HITL) interactive analysis, an asynchronous
FastAPI + Celery + Redis pipeline, and a React-based admin panel.

> Backend: `agents/`, `api/`, `tasks/`, `shared/` — Frontend: `admin_pan/Admin/src/rca-frontend/`
> Production deployment: Railway (API + Worker + Redis), admin panel on Vercel.

## High-Level Architecture

```
                         ┌────────────────────────────┐
                         │   Admin Panel (Vercel)     │
                         │  admin_pan/Admin           │
                         │  src/rca-frontend          │
                         └─────────────┬──────────────┘
                                       │  REST + WebSocket
                                       ▼
                         ┌────────────────────────────┐
                         │   FastAPI (api/main.py)    │
                         │  Multitenant + HITL + Jobs │
                         └─────────────┬──────────────┘
            ┌──────────────────────────┼──────────────────────────┐
            ▼                          ▼                          ▼
   ┌────────────────┐         ┌────────────────┐         ┌────────────────┐
   │ Overview /     │         │ Hybrid Cache   │         │ Celery Worker  │
   │ Assessment     │         │ Redis + Mongo  │         │ tasks/         │
   │ Agents         │         │ + Tenant Store │         │ pipeline_tasks │
   └────────────────┘         └────────────────┘         └────────┬───────┘
                                                                  ▼
                                                  ┌──────────────────────────────┐
                                                  │ RootCauseAgentV3.1 (DSPy)    │
                                                  │ + BranchCritic + ActionPlan  │
                                                  │ + SkillBasedDocxAgent (DOCX) │
                                                  └──────────────────────────────┘
```

## 📂 Project Structure

```
HSE_RCAnalysis_AgenticAI/
├── agents/                          # AI agents (HSG245 4-Part flow)
│   ├── overview_agent.py            # Part 1 — Overview
│   ├── assessment_agent.py          # Part 2 — Initial Assessment
│   ├── rootcause_agent_v3_1.py      # Part 3 — DSPy 5-Why (active)
│   ├── rootcause_agent_v2.py        # Part 3 — V2 fallback
│   ├── branch_critic.py             # Cross-branch duplication guard
│   ├── actionplan_agent.py          # Part 4 — Action Plan
│   ├── skillbased_docx_agent.py     # DOCX reports (OpenRouter)
│   ├── claude_skill_pdf_agent.py    # PDF reports
│   ├── orchestrator.py              # Pipeline coordinator
│   ├── pattern_analyzer.py          # Tenant root-cause analytics
│   ├── hitl_question_service.py     # Dynamic HITL question generation
│   ├── hitl_disambiguation_bank.py  # HSG245 disambiguation templates
│   ├── knowledge_base.py            # HSG245 taxonomy
│   ├── model_constants.py           # OpenRouter model resolution
│   ├── synetic_data_preperation/    # Synthetic data for DSPy MIPRO
│   └── v3_vector_search/            # RAG (experimental)
│
├── api/
│   └── main.py                      # FastAPI: incident, HITL, pipeline, WS
├── tasks/
│   └── pipeline_tasks.py            # Celery tasks (Part3 + Part4)
├── shared/
│   ├── tenant_store.py              # Multi-tenant in-memory store
│   ├── tenant_auth.py               # X-Tenant-ID / X-API-Key resolver
│   ├── hybrid_cache.py              # L1 Redis + L2 MongoDB cache
│   ├── oracle_memory.py             # Per-tenant context (Mongo)
│   ├── redis_client.py              # Redis helpers
│   └── ops_celery.py                # Celery introspection
├── celery_app.py                    # Celery app + broker config
├── hitl_test/                       # HITL experiments + question engine
│
├── admin_pan/                       # Admin panel (submodule)
│   └── Admin/src/rca-frontend/
│       ├── RcaFrontendHub.jsx       # Form + interactive analysis host
│       ├── components/
│       │   ├── IncidentForm.jsx     # Manual form
│       │   ├── ChatInterface.jsx    # HITL + live pipeline flow
│       │   ├── QuestionFlow.jsx     # Legacy fixed question flow
│       │   ├── Message.jsx          # Chat message UI
│       │   └── Header.jsx
│       └── utils/
│           ├── investigationPayload.js
│           ├── hitlKbQuestions.js
│           └── translations.js
│       └── ../services/
│           ├── hsg245Api.js         # REST + WS gateway client
│           └── agentApi.js
│
├── outputs/                         # Test outputs (HTML, DOCX, JSON)
├── tests/                           # Scenario-based integration tests
├── requirements.txt
├── Procfile                         # Railway: web (uvicorn)
├── Procfile.worker                  # Railway: worker (celery)
├── scripts/railway_celery_worker.sh
└── railway.json
```

## 🤖 Core Agents (HSG245 4-Part Flow)

| Step | Agent | Responsibility |
| ---- | ---- | ----- |
| Part 1 | `OverviewAgent` | Structure incident basics (ref no, datetime, brief details). |
| Part 2 | `AssessmentAgent` | Type, severity, RIDDOR, investigation level. |
| Part 3 | `RootCauseAgentV3_1` (DSPy) | A/B immediate causes + 5-Why branches + C/D root causes. |
| Part 3+ | `BranchCriticAgent` | Cross-branch duplicate detection + LLM regenerate. |
| Part 4 | `ActionPlanAgent` | Immediate/Short/Long-term action planning. |
| Report | `SkillBasedDocxAgent` / `ClaudeSkillPDFAgent` | DOCX/PDF report generation. |

V3.1 architecture:

```
RootCauseAgentV3_1
├── ImmediateCauseFinder        (A/B categories)
├── WhyChain                    (DSPy 5-Why module)
│   ├── SemanticAnswerVerifier  (in-chain repetition guard)
│   ├── WhyQuestion / WhyAnswer (type-safe)
│   └── RootCauseValidator      (C/D validation)
├── MetaRootCauseSynthesizer    (shared systemic root)
└── BranchCriticAgent           (cross-branch critic + regenerate)
```

If `RootCauseAgentV3_1` import/init fails, the system automatically falls back to
`RootCauseAgentV2` (`agents/__init__.py`).

## 🌐 FastAPI Backend (`api/main.py`)

Main endpoints (multi-tenant with `X-Tenant-ID` or `X-API-Key`):

| Method | Path | Description |
| ------ | ---- | -------- |
| `POST` | `/api/v1/incidents/create` | Part 1 — create incident |
| `POST` | `/api/v1/incidents/{id}/assessment` | Part 2 — assessment |
| `POST` | `/api/v1/incidents/{id}/hitl/questions` | Dynamic HITL question batch (global / why_probe) |
| `POST` | `/api/v1/incidents/{id}/investigate` | Part 3 — synchronous RCA (fallback path) |
| `POST` | `/api/v1/incidents/{id}/pipeline/start` | Part 3 + Part 4 async job (Celery) |
| `GET`  | `/api/v1/jobs/{job_id}` | Job status (in-process or Celery) |
| `WS`   | `/ws/jobs/{job_id}` | Job progress streaming |
| `POST` | `/api/v1/incidents/{id}/actionplan` | Part 4 — action plan |
| `GET`  | `/api/v1/incidents/{id}` | Get incident |
| `GET`  | `/api/v1/incidents` | List incidents |
| `POST` | `/api/v1/oracle/context` | Write tenant context |
| `GET`  | `/api/v1/oracle/context` | Read tenant context |
| `GET`  | `/api/v1/analytics/patterns` | Root cause code analytics |
| `POST` | `/api/v1/incidents/{id}/pdf` | Generate PDF report |
| `GET`  | `/api/v1/health` | Health + agent status |

Tenant resolution priority (`shared/tenant_auth.py`):
1. `X-API-Key` → `TENANT_API_KEYS_JSON` map (`{"sk-xxx": "tenant_slug"}`)
2. `X-Tenant-ID` header
3. `default`

Incidents are persisted in both tenant in-memory store and Redis
(`hse:incident:{tenant}:{id}`) for cross-instance consistency.

## 🧠 Celery Pipeline (`tasks/pipeline_tasks.py`)

`pipeline_start` submits `run_pipeline_task` to the worker through Redis broker.
Worker:

1. `RootCauseAgentV3_1.analyze_root_causes(part1, part2, investigation)` — Part 3
2. `ActionPlanAgent.generate_action_plan(...)` — Part 4
3. Publishes stage/progress via `update_state(stage=investigate|actionplan|completed, ...)`
4. API syncs incident store using result payload + `tenant_id`

Frontend `runPipelineJobWithPolling` first attempts WebSocket progress; if unavailable,
it falls back to HTTP polling.

## 🎨 Frontend (`admin_pan/Admin/src/rca-frontend/`)

Two-tab React experience hosted by `RcaFrontendHub.jsx`:

- **Manual Form (`IncidentForm.jsx`)**: HSG245-aligned, sectioned form with
  test-scenario prefill support (`utils/testScenarios.js`).
- **Interactive Analysis (`ChatInterface.jsx`)**: After form submission:
  1. Runs `createIncident` (Part 1) + `addAssessment` (Part 2).
  2. Switches to chat using `hitlSeed` prop.
  3. Calls `fetchHitlQuestions` for ordered HSG245 disambiguation + taxonomy-gap
     question batches (`global` or `why_probe` mode).
  4. Requests the next question after each answer; depth advances 1→5 per branch.
  5. Starts Part 3 + Part 4 with `runPipelineJobWithPolling` when questions are done.
  6. Shows live stages over WebSocket (`Queued → Investigate → ActionPlan → Completed`).
  7. Allows report generation (`generatePDFReport`) after completion.

REST + WS client: `admin_pan/Admin/src/services/hsg245Api.js`.
Helpers: `utils/investigationPayload.js`, `utils/hitlKbQuestions.js`.

## 🛠️ HITL (Human-in-the-Loop) Flow

`agents/hitl_question_service.py` supports two modes:

- **global**: `build_hitl_question_pool` — disambiguation + missing taxonomy questions.
- **why_probe**: `build_why_probe_question_pool` — focused follow-up questions at each
  Why level (1..5) for selected immediate code(s).

Answers are transformed into `why_probe_answers` and injected into Part 3 RCA,
so the model can reach incident-specific depth.

## 🌍 Multi-Tenant + Context

- `shared/tenant_store.py` keeps isolated `incidents_db` and `jobs_db` per tenant.
- `shared/hybrid_cache.py` provides tenant-namespaced L1 Redis + L2 MongoDB cache
  (for HITL and derived payloads).
- `shared/oracle_memory.py` stores long-lived tenant context (MongoDB), injected into
  RCA requests (`merge_oracle_into_investigation`).

## 🚀 Kurulum

### Prerequisites

- Python 3.11+
- Node.js 18+
- Redis (Docker locally recommended)
- Optional: MongoDB (hybrid cache + oracle context)
- OpenRouter API key (`OPENROUTER_API_KEY`)

### Backend

```bash
git clone --recurse-submodules https://github.com/selcuk-yalcin/HSE_RCAnalysis_AgenticAI.git
cd HSE_RCAnalysis_AgenticAI

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env  # OPENROUTER_API_KEY, REDIS_URL, MONGODB_URI, etc.

# API
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Celery worker (separate terminal)
sh scripts/railway_celery_worker.sh
# veya:
python -m celery -A celery_app:celery_app worker --loglevel=info --concurrency=1 --pool=solo
```

### Admin Panel

```bash
cd admin_pan/Admin
npm install
npm run dev    # http://localhost:5173
```

### Key Environment Variables

| Variable | Description |
| -------- | -------- |
| `OPENROUTER_API_KEY` | Required for LLM calls |
| `OPENROUTER_BASE_URL` | Default `https://openrouter.ai/api/v1` |
| `OPENROUTER_DSPY_MODEL` | e.g. `google/gemini-2.5-flash` |
| `OPENROUTER_DOCX_MODEL` | Model for DOCX report generation |
| `OPENROUTER_MODEL_PRESET` | `flash` / `sonnet` |
| `REDIS_URL` | Celery broker + cache |
| `MONGODB_URI` | Hybrid cache + oracle (optional) |
| `INCIDENT_REDIS_TTL_SECONDS` | Incident cache TTL |
| `TENANT_API_KEYS_JSON` | `{"sk-...": "tenant_slug"}` mapping |
| `ROOTCAUSE_USE_RAG` | Enable RAG with `1` (experimental) |
| `ROOTCAUSE_ENGINE` | Force `v2` engine |
| `CELERY_POOL` / `CELERY_CONCURRENCY` | Worker tuning |
| `CELERY_AUTOSCALE_MAX` / `CELERY_AUTOSCALE_MIN` | Prefork autoscale range |
| `CELERY_VISIBILITY_TIMEOUT` | Redis visibility timeout for long tasks |
| `CELERY_HEARTBEAT_INTERVAL` | Worker heartbeat interval |
| `CELERY_DISABLE_MINGLE` / `CELERY_DISABLE_GOSSIP` | Reduce cross-worker heartbeat drift warnings |
| `CELERY_WORKER_UID` | Run worker as non-root user (default `1000`) |

## 🔁 Development Workflow

```bash
# Backend changes
git add agents/ api/ shared/ tasks/ celery_app.py
git commit -m "feat: ..."
git push origin main

# Admin panel (submodule)
cd admin_pan
git add . && git commit -m "feat: ..." && git push origin main
cd ..
git add admin_pan && git commit -m "chore: bump admin submodule" && git push
```

## 🧪 Tests

Scenario-based integration tests under `tests/`:

- `test_train_odor_incident_dspy.py`
- `test_high_potential_near_miss_dspy.py`
- `test_property_damage_dspy.py`
- `test_ak05_yuksekten_dusme_dspy.py`
- `test_undesired_circumstance_dspy.py`

Set `OPENROUTER_API_KEY` or `OPENAI_API_KEY` before running tests.

```bash
python tests/test_train_odor_incident_dspy.py
```

## 🧭 Spec-Driven Development

This project follows a spec-driven workflow in Cursor.

- Core specs live under `specs/`:
  - `specs/plan.md`
  - `specs/roadmap.md`
  - `specs/tech-stack.md`
  - `specs/README.md`
- Cursor rule: `.cursor/rules/spec-driven-workflow.mdc` (`alwaysApply: true`)
- Recommended change flow:
  1. Align scope with `specs/plan.md` and `specs/roadmap.md`
  2. Update specs for non-trivial changes
  3. Implement code
  4. Sync docs/specs after implementation

## 📈 Roadmap

See `TODO.md` for the active roadmap
(multi-tenant user management, synthetic data + MIPROv2, frontend streaming,
HITL depth, etc.).

## License

MIT License

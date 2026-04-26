# Product and Architecture Plan

## Product Goal

DeepWhy is an HSG245-based multi-agent Root Cause Analysis platform that combines:

- Structured incident intake,
- Interactive Human-in-the-Loop (HITL) questioning,
- DSPy-powered 5-Why root cause analysis,
- Action planning and report generation (PDF/DOCX),
- Multi-tenant API and async execution.

## Core User Flows

1. User submits incident form (Part 1 + Part 2 bootstrap).
2. HITL questioning refines context with incident-specific prompts.
3. Async pipeline starts (Part 3 + Part 4).
4. User observes progress via WebSocket/polling.
5. User exports report artifacts.

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

## Spec Ownership

- Product + flow details: `README.md`
- Execution backlog: `specs/roadmap.md`
- Stack and runtime constraints: `specs/tech-stack.md`

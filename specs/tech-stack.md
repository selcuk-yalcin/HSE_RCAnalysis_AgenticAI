# Tech Stack and Runtime Map

## Backend Runtime

- Python 3.11+
- FastAPI (`api/main.py`)
- Celery + Redis (`celery_app.py`, `tasks/pipeline_tasks.py`)
- Optional MongoDB (`shared/hybrid_cache.py`, `shared/oracle_memory.py`)

## AI / LLM Layer

- OpenRouter as primary provider.
- OpenAI-compatible SDK usage in multiple agents.
- DSPy for V3.1 root cause engine and modular reasoning chains.
- Branch critic module for cross-branch duplication control.

## Frontend Runtime

- React-based admin app under `admin_pan/Admin/`.
- Interactive RCA flow in `src/rca-frontend/`.
- REST + WebSocket integration through `src/services/hsg245Api.js`.

## Persistence and Caching

- Tenant-scoped in-memory stores (`shared/tenant_store.py`).
- Redis for broker, result backend, and cache.
- Hybrid cache strategy: Redis L1 + Mongo L2.

## Deployment

- Railway:
  - API service (`uvicorn api.main:app`)
  - Worker service (`python -m celery -A celery_app:celery_app worker ...`)
  - Redis service
- Vercel for admin panel.

## Build/Operations Constraints

- Keep worker startup deterministic and observable.
- Avoid heavy dependencies unless explicitly required in production.
- Preserve fallback behavior if DSPy/V3.1 fails to initialize.

## Current Risks to Track

- OpenRouter authentication consistency in worker runtime.
- Frontend-to-backend tenant propagation consistency.
- Streaming UX degradation when WebSocket is unavailable.

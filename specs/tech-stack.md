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
- **P1.15 (done):** per-user token accounts + append-only token ledger in Mongo (`shared/token_account.py`); usage API; enforcement in FastAPI + pipeline; Dashboard + DeepWhy token strip in `admin_pan`.
- **P1.16:** Rapor Rehberi tab — static/cdn video via `VITE_RCA_GUIDE_VIDEO_URL` or `public/media/rca-report-guide/report-guide.mp4`.
- Vector retrieval for RAG (Railway target):
  - Primary store: MongoDB Atlas Vector Search (`rca.taxonomy` style collections).
  - Embeddings: managed API embeddings preferred for production cost/runtime stability.
  - Avoid local file-based vector stores for production worker pods.

## Deployment

- Railway:
  - API service (`uvicorn api.main:app`) — prefer slim **`Dockerfile`** build (`builder: DOCKERFILE` in `railway.json`); image copies `api`, `agents`, `hitl_test`, `shared`, `tasks`, `rag_pipeline`, `scripts`.
  - Worker service (`sh scripts/railway_celery_worker.sh` or equivalent Celery worker command)
  - Worker scaling policy:
    - `CELERY_POOL=prefork`
    - `--autoscale=5,1` via `CELERY_AUTOSCALE_MAX=5`, `CELERY_AUTOSCALE_MIN=1`
    - Expected behavior: idle load keeps 1 process; queued load scales up to 5
  - Reliability tuning targets:
    - Celery heartbeat tolerance for long RCA tasks
    - Redis broker visibility timeout aligned with long-running pipeline jobs
    - Avoid single-worker CPU starvation in heavy sections
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
- Action-plan LLM outputs occasionally violate strict JSON; parser hardening/retry is required.

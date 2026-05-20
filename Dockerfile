# Slim Railway image — avoids Railpack/Nixpacks disk exhaustion on cold builds.
# Agents: default CMD (uvicorn). Worker: override start command in Railway:
#   sh scripts/railway_celery_worker.sh

FROM python:3.11-slim-bookworm AS deps

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-railway.txt .
RUN pip install -r requirements-railway.txt

FROM python:3.11-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

COPY api api
COPY agents agents
COPY hitl_test hitl_test
COPY shared shared
COPY tasks tasks
COPY rag_pipeline rag_pipeline
COPY celery_app.py .
COPY scripts scripts

EXPOSE 8000

CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

#!/usr/bin/env sh
# Railway / Nixpacks: use python -m celery so the CLI is always on PYTHONPATH.
# CELERY_POOL=solo avoids prefork issues on small containers (default: prefork).
set -eu
POOL="${CELERY_POOL:-solo}"
LOGLEVEL="${CELERY_LOGLEVEL:-info}"
CONCURRENCY="${CELERY_CONCURRENCY:-2}"
exec python -m celery -A celery_app:celery_app worker --loglevel="$LOGLEVEL" --concurrency="$CONCURRENCY" --pool="$POOL"

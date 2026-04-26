#!/usr/bin/env sh
# Railway / Nixpacks: use python -m celery so the CLI is always on PYTHONPATH.
# Autoscale defaults keep low idle cost: min=1, max=5.
set -eu
POOL="${CELERY_POOL:-prefork}"
LOGLEVEL="${CELERY_LOGLEVEL:-info}"
AUTOSCALE_MAX="${CELERY_AUTOSCALE_MAX:-5}"
AUTOSCALE_MIN="${CELERY_AUTOSCALE_MIN:-1}"

exec python -m celery -A celery_app:celery_app worker \
  --loglevel="$LOGLEVEL" \
  --pool="$POOL" \
  --autoscale="$AUTOSCALE_MAX,$AUTOSCALE_MIN"

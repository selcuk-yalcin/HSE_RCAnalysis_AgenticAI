#!/usr/bin/env sh
# Railway / Nixpacks: use python -m celery so the CLI is always on PYTHONPATH.
# Autoscale defaults keep low idle cost: min=1, max=5.
set -eu
POOL="${CELERY_POOL:-prefork}"
LOGLEVEL="${CELERY_LOGLEVEL:-info}"
AUTOSCALE_MAX="${CELERY_AUTOSCALE_MAX:-5}"
AUTOSCALE_MIN="${CELERY_AUTOSCALE_MIN:-1}"
HEARTBEAT_INTERVAL="${CELERY_HEARTBEAT_INTERVAL:-30}"
WORKER_UID="${CELERY_WORKER_UID:-1000}"
DISABLE_MINGLE="${CELERY_DISABLE_MINGLE:-1}"
DISABLE_GOSSIP="${CELERY_DISABLE_GOSSIP:-1}"

EXTRA_FLAGS=""
if [ "${DISABLE_MINGLE}" = "1" ]; then
  EXTRA_FLAGS="${EXTRA_FLAGS} --without-mingle"
fi
if [ "${DISABLE_GOSSIP}" = "1" ]; then
  EXTRA_FLAGS="${EXTRA_FLAGS} --without-gossip"
fi

exec python -m celery -A celery_app:celery_app worker \
  --loglevel="$LOGLEVEL" \
  --pool="$POOL" \
  --autoscale="$AUTOSCALE_MAX,$AUTOSCALE_MIN" \
  --heartbeat-interval="$HEARTBEAT_INTERVAL" \
  --uid="$WORKER_UID" \
  $EXTRA_FLAGS

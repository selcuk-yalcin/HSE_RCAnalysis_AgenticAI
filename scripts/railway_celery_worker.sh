#!/usr/bin/env sh
# Railway / Nixpacks: use python -m celery so the CLI is always on PYTHONPATH.
# Autoscale defaults keep low idle cost: min=1, max=5.
# macOS local: CELERY_WORKER_UID=  and  pip install -r requirements.txt
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${ROOT}${PYTHONPATH:+:$PYTHONPATH}"

if [ -f "$ROOT/.env" ]; then
  _ENV_EXPORTS="$(_ENV_FILE="$ROOT/.env" python - <<'PY' 2>/dev/null || true
import os, shlex
from pathlib import Path
try:
    from dotenv import dotenv_values
except ImportError:
    raise SystemExit(0)
path = Path(os.environ["_ENV_FILE"])
for k, v in (dotenv_values(path) or {}).items():
    if v is not None and str(v).strip() != "":
        print(f"export {k}={shlex.quote(str(v))}")
PY
)"
  if [ -n "$_ENV_EXPORTS" ]; then
    eval "$_ENV_EXPORTS"
  fi
fi

python -c "import redis" 2>/dev/null || {
  echo "ERROR: Python redis package missing for $(command -v python)."
  echo "  pip install 'redis>=5.0.0' 'celery>=5.3.0'"
  echo "  or: pip install -r requirements.txt"
  exit 1
}

export TZ="${TZ:-UTC}"
POOL="${CELERY_POOL:-prefork}"
LOGLEVEL="${CELERY_LOGLEVEL:-info}"
AUTOSCALE_MAX="${CELERY_AUTOSCALE_MAX:-5}"
AUTOSCALE_MIN="${CELERY_AUTOSCALE_MIN:-1}"
HEARTBEAT_INTERVAL="${CELERY_HEARTBEAT_INTERVAL:-30}"
# Default uid=1000 for Linux/Railway. macOS local: CELERY_WORKER_UID= (empty) to skip --uid.
WORKER_UID="${CELERY_WORKER_UID-1000}"
DISABLE_MINGLE="${CELERY_DISABLE_MINGLE:-1}"
DISABLE_GOSSIP="${CELERY_DISABLE_GOSSIP:-1}"

UID_ARG=""
if [ -n "$WORKER_UID" ]; then
  UID_ARG="--uid=$WORKER_UID"
fi

EXTRA_FLAGS=""
if [ "${DISABLE_MINGLE}" = "1" ]; then
  EXTRA_FLAGS="${EXTRA_FLAGS} --without-mingle"
fi
if [ "${DISABLE_GOSSIP}" = "1" ]; then
  EXTRA_FLAGS="${EXTRA_FLAGS} --without-gossip"
fi

echo "worker-start tz=${TZ} utc_now=$(date -u +"%Y-%m-%dT%H:%M:%SZ") pool=${POOL} autoscale=${AUTOSCALE_MAX},${AUTOSCALE_MIN} heartbeat=${HEARTBEAT_INTERVAL}"

exec python -m celery -A celery_app:celery_app worker \
  --loglevel="$LOGLEVEL" \
  --pool="$POOL" \
  --autoscale="$AUTOSCALE_MAX,$AUTOSCALE_MIN" \
  --heartbeat-interval="$HEARTBEAT_INTERVAL" \
  $UID_ARG \
  $EXTRA_FLAGS

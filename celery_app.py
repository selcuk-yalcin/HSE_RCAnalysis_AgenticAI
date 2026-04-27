"""
Project-level Celery application.
"""

from __future__ import annotations

import os

from celery import Celery

# Worker startup fingerprint — bump on each deploy verification cycle so logs
# clearly show whether the running container has the latest code.
WORKER_BUILD_TAG = "rca-worker@2026-04-25T15:30Z openrouter-headers-v3"
print(f"🛠️  Celery worker module loaded — build={WORKER_BUILD_TAG}")


REDIS_URL = (os.getenv("REDIS_URL") or "redis://localhost:6379/0").strip()
BROKER_HEARTBEAT = int((os.getenv("CELERY_BROKER_HEARTBEAT") or "30").strip() or "30")
BROKER_POOL_LIMIT = int((os.getenv("CELERY_BROKER_POOL_LIMIT") or "10").strip() or "10")
VISIBILITY_TIMEOUT = int((os.getenv("CELERY_VISIBILITY_TIMEOUT") or "7200").strip() or "7200")
HEALTH_CHECK_INTERVAL = int((os.getenv("CELERY_HEALTH_CHECK_INTERVAL") or "20").strip() or "20")

celery_app = Celery(
    "hse_rca_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks.pipeline_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,
    task_soft_time_limit=1500,
    result_expires=3600,
    broker_heartbeat=BROKER_HEARTBEAT,
    broker_heartbeat_checkrate=2,
    broker_pool_limit=BROKER_POOL_LIMIT,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=None,  # keep retrying on transient Railway/Redis blips
    broker_transport_options={
        "socket_connect_timeout": 30,
        "socket_timeout": 30,
        "socket_keepalive": True,
        "retry_on_timeout": True,
        "health_check_interval": HEALTH_CHECK_INTERVAL,
        "visibility_timeout": VISIBILITY_TIMEOUT,
    },
    worker_prefetch_multiplier=1,
)


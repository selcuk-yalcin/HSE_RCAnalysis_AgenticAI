# Execution Roadmap

Source: synchronized from root `TODO.md`.

## P0 (Critical)

### P0.1 Multi-Tenant User Management

- Persistent tenant/user registry in Redis.
- Admin tenant and user management APIs.
- Role-based authorization on pipeline and incident operations.
- Frontend tenant header propagation.

### P0.2 5-Step Incident-Specific HITL

- Add LLM-driven incident-specific HITL question generator.
- Remove generic first-step prompts; start with incident summary + analysis notice.
- After first immediate-cause stage, generate deeper selectable questions from `agents/knowledge_base.py`.
- Fallback from static logic to LLM by quality threshold.
- Improve Why-chain continuity and answer handling options.
- Persist HITL logs for training reuse.
- Keep a single primary large-area frontend analysis flow (remove duplicated secondary Why widgets).

### P0.3 Frontend Live Streaming

- Branch/why-level granular progress callbacks.
- Enriched job payload fields for UI.
- Live timeline component in chat UI.
- WebSocket reconnect and robust failure UX.

### P0.4 Worker OpenRouter 401 Stabilization

- Eliminate `Missing Authentication header` failures in Step 3 (Celery worker).
- Enforce deploy/runtime parity between API and worker services.
- Add deterministic startup diagnostics for auth/debug visibility.
- Verify worker is running latest commit via build fingerprint and deploy metadata.
- Add clear runbook for Railway redeploy + env parity checks.
- Acceptance:
  - Worker logs show build fingerprint and OpenRouter runtime config on startup.
  - HITL flow reaches Part 3+Part 4 completion without OpenRouter 401.
  - Same env/config behavior is reproducible after restart and redeploy.

### P0.5 Worker Burst Scaling Without Always-On High Load

- Configure Celery worker autoscaling for burst traffic.
- Default runtime profile:
  - `CELERY_POOL=prefork`
  - `CELERY_AUTOSCALE_MAX=5`
  - `CELERY_AUTOSCALE_MIN=1`
- Keep baseline resource usage low while allowing temporary parallel RCA jobs.
- Acceptance:
  - Idle worker runs at min process count.
  - Under queue pressure worker scales up to configured max.
  - Scale-down occurs automatically after queue drains.

### P0.6 Action Plan JSON Robustness

- Enforce stricter Action Plan JSON schema validation.
- Add retry and \"json-only\" sanitizer parser for malformed outputs.
- Sanitize markdown fences and trailing commas before parsing.
- Add parse telemetry and malformed-output regression tests.

### P0.7 Celery Long-Run Reliability

- Keep `prefork + autoscale` as baseline worker runtime.
- Tune heartbeat and broker visibility timeout for long RCA tasks.
- Reduce single-worker CPU blocking with staged checkpoints.
- Add 3-5 parallel-run reliability/load validation and ops visibility.

## P1 (Near-Term)

### P1.1 Synthetic Data Pipeline

- Mongo output mode for synthetic generation.
- Tenant partitioning and seeded generation from incidents.
- Scheduled generation jobs and admin trigger endpoint.

### P1.2 DSPy MIPROv2 Integration

- Define RCA quality metrics.
- Build optimize/compile pipeline for WhyChain.
- Version compiled artifacts and support runtime loading.
- Add baseline vs compiled A/B evaluation.

### P1.3 Operational Training Workflow

- Standardize train/eval/promote commands.
- Store run artifacts and lineage metadata.
- Nightly CI training with release gate.

### P1.4 Tenant Insights

- Time trends, severity and category distributions.
- Department/location analytics breakdown.
- Dashboard visualization in admin panel.

### P1.5 RAG Rollout

- Managed embeddings and vector store.
- Tenant-isolated vector namespaces.
- Controlled RAG prompt injection strategy.

## P2 (Mid-Term)

### P2.1 Voice Input

- Incident voice capture and STT integration.

### P2.2 Language Strategy

- Output language consistency and broader locale support.

### P2.3 Test Coverage

- Unit tests for tenant/cache/HITL services.
- CI mocking for LLM interfaces.
- Playwright e2e flow validation.

### P2.4 Observability

- Structured logging, latency/token metrics, Sentry/Highlight.

## Continuous

- Bump worker build fingerprint every release.
- Maintain key rotation playbook.
- Archive legacy agent versions.
- Exclude generated outputs from git tracking.

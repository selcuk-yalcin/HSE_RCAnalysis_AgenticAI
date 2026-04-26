# Execution Roadmap

Source: synchronized from root `TODO.md`.

## P0 (Critical)

### P0.1 Multi-Tenant User Management

- Persistent tenant/user registry in MongoDB.
- Admin tenant and user management APIs.
- Role-based authorization on pipeline and incident operations.
- Frontend tenant header propagation.

### P0.2 5-Step Incident-Specific HITL

- Add LLM-driven incident-specific HITL question generator.
- Fallback from static logic to LLM by quality threshold.
- Improve Why-chain continuity and answer handling options.
- Persist HITL logs for training reuse.

### P0.3 Frontend Live Streaming

- Branch/why-level granular progress callbacks.
- Enriched job payload fields for UI.
- Live timeline component in chat UI.
- WebSocket reconnect and robust failure UX.

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

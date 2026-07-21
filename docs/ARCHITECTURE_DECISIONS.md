# Part 2 Architecture Decisions

## Purpose
This file records decisions that must survive agent changes and conversation compaction.

## ADR-001: Build a Thin Purpose-Built Application

### Status
Accepted

### Decision
Do not adopt a pre-built contract-review application as the foundation of the prototype.

Build the Legal workflow as a thin application using mature open-source infrastructure components:
- React/TypeScript/Vite frontend
- FastAPI backend
- Haystack pipeline orchestration
- Document parsing (P1: `pypdf`/`python-docx`; Docling remains the target once P6
  model-artifact pre-provisioning exists — Docling was spiked in P1 and rejected for
  requiring a network model download even with OCR disabled; see
  `TECH_STACK_AND_LICENSES.md` and `RISK_REGISTER.md` R-05)
- Qdrant vector storage for supplemental guidance retrieval
- A provider-neutral model adapter
- The defense playbook and structured output contract defined in this folder

### Reason
Contract-specific repositories may offer a faster-looking start, but their deployment assumptions, security posture, hidden integrations, and fit to the required deterministic workflow are not sufficiently predictable for a two-day build. A thin application gives direct control over the workflow, data flow, UI, and case-study narrative.

### Consequences
- We still use established open-source repositories as components.
- We do not inherit a pre-cooked contract-review product or its UI.
- Domain behavior must be implemented from the local specifications.
- The prototype remains small enough to replace individual components later.

## ADR-002: Provider-Neutral Model Integration

### Status
Accepted for prototype planning. As of the hosted handoff update, the public
Render demo uses the same Ollama adapter when `PART2_OLLAMA_BASE_URL` points
to a Render-reachable endpoint; no proprietary/cloud model adapter is
implemented.

### Decision
The application must expose one internal model interface. The admin screen may configure an Ollama-compatible endpoint or an approved cloud provider for the hosted demonstration.

The target enterprise architecture is on-premises and uses Ollama or another locally hosted compatible runtime. If a cloud model is used for the public demo, it must be labelled `Demo mode` and must use synthetic, non-sensitive documents only.

### Consequences
- Provider-specific code cannot leak into the review pipeline.
- API keys remain server-side and must never be returned by configuration APIs.
- Cloud demo capability is not evidence that cloud processing is suitable for production.

## ADR-003: Structured Pipeline, Not Chat

### Status
Accepted

### Decision
The application executes a fixed sequence: parse, segment, classify, compare with playbook, validate, and render structured findings. There is no conversational loop and no chatbot UI.

### Consequences
- Every model output must pass schema validation.
- Rule-based checks and missing-clause detection remain explicit application stages.
- The system records evidence text and rule identifiers for auditability.

## ADR-004: Deterministic Rules Own Risk Decisions

### Status
Accepted

### Decision
Models extract and normalize evidence. Versioned application rules select findings, severities, and overall risk. Retrieval, if enabled, cannot exclude rules or act as an authority.

### Reason
This preserves explainability and stable risk decisions while still using local AI for document understanding.

## ADR-005: Reference Local Models

### Status
Accepted

### Decision
Use Docker-based Ollama with `qwen3:4b` as the lightweight Apache-2.0 PoC LLM reference and `intfloat/multilingual-e5-small` as the MIT local embedding model. Larger permissively licensed local models, such as Qwen2.5-7B-Instruct, remain optional validation candidates if the lightweight model fails the golden fixture.

### Reason
Both fit the permissive-license requirement and can operate within the local stack. Docker-based Ollama keeps the PoC runtime isolated and removable after the demo. The embedding model supports multilingual retrieval, but Indonesian quality still requires testing. Final suitability must be verified against the golden fixture and language-preservation checks.

## ADR-006: Prototype Persistence

### Status
Accepted

### Decision
Use SQLite for review records and Qdrant only for vectors. Preserve repository boundaries so enterprise deployment can replace SQLite with PostgreSQL.

## ADR-009: Prototype Job Runner

### Status
Accepted

### Decision
Use a bounded in-process FastAPI background executor for the one-instance PoC. Treat a backend restart as an interruption: active jobs must recover as `failed` with `JOB_INTERRUPTED`. The enterprise target may replace this with a dedicated queue and worker.

### Reason
This keeps the two-day prototype small while preserving an explicit reliability boundary and a migration path.

## ADR-010: Hosted Demo Controls

### Status
Accepted

### Decision
Use restricted hosted access for the demo, with synthetic data only. Provider credentials use environment bootstrap plus a write-only in-memory admin override for Demo mode. Saved credentials must never be returned by APIs, persisted in SQLite, logged, or included in review results.

### Reason
The hosted demo is for presentation access, not production data handling. It must demonstrate configurability without weakening the on-premises target architecture.

## ADR-011: Results Display

### Status
Accepted

### Decision
Show High and Critical findings prominently. Show compliant Low findings collapsed by default so the demo proves coverage without distracting from risk triage.

## ADR-007: Monorepo

### Status
Accepted

### Decision
Use one repository rooted at `Part2/` for frontend, backend, playbooks, fixtures, tests, deployment assets, and specifications. Follow `REPOSITORY_STRATEGY.md`.

### Reason
The two-day build requires atomic API/schema changes, one local environment, one deployment definition, and simple agent handoffs.

## ADR-008: Language Scope

### Status
Accepted for MVP planning

### Decision
Use the English synthetic golden fixture for deterministic acceptance. Do not hardcode English into parsing, storage, schemas, or prompts. Preserve Indonesian and other Unicode text end to end. An Indonesian synthetic smoke test is desirable if time permits but is not a release blocker for the two-day PoC.

### Consequence
Production multilingual claims require a bilingual playbook, Indonesian legal review, and separate model-quality evaluation.

## ADR-012: Hosted Demo Deployment Topology

### Status
Accepted (P7)

### Decision
The hosted demo (D-07: Render, Docker Web Service) is model-capable through
Ollama when `PART2_OLLAMA_BASE_URL` points to a Render-reachable endpoint.
Qdrant remains absent from the hosted environment, so supplemental guidance
degrades cleanly. Frontend and backend are served **same-origin** from one container:
`backend/Dockerfile.hosted` builds the frontend and copies its static
output into the backend image, which serves it via a catch-all SPA-fallback
route registered after the API routers. Access is gated by an app-level
HTTP Basic Auth middleware active only when `deployment_mode: demo`
(D-06), and `PUT /config` is backend-locked in that mode regardless of the
frontend nav visibility. SQLite persistence on the hosted demo
is ephemeral on Render's free plan (no persistent disk on that tier) — an
explicit, disclosed demo-only exception (see `docs/SECURITY_EVIDENCE.md`
section 10).

### Reason
This keeps the hosted demo a thin packaging exercise on top of the existing
architecture rather than a second product surface: no new cross-origin
attack surface, no proprietary cloud model adapter, and a single
Dockerfile that never touches `docker-compose.yml`, local ports, or the
default deterministic dev flow.

### Consequences
- The hosted demo can demonstrate the P3 model-assisted path if Render can
  reach the configured Ollama endpoint. It cannot reach private LAN IPs such
  as `192.168.x.x`; use an approved public/VPN/tunnel route when live hosted
  model execution is required.
- The hosted demo does not demonstrate the P4 Qdrant retrieval path live;
  retrieval remains evidenced by local Docker Qdrant verification.
- A future real hosted persistence decision
  would need its own explicit acceptance and is out of scope for P7.

## Change Rule
Do not reverse or materially alter an accepted decision without updating this file, `MASTER_INDEX.md`, `PLAN.md`, and every affected specification.

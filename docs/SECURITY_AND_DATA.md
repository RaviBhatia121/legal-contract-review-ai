# Part 2 Security and Data Rules

## Security Position
The prototype demonstrates a security-conscious architecture; it is not certified for classified or production defense data.

## Demo Data Rule
- Use synthetic contracts only.
- Never upload client, classified, export-controlled, privileged, or otherwise sensitive material to the hosted demo.
- If a cloud model is active, display a visible `Demo mode - synthetic data only` notice.

## Required Controls
- Validate file extension, MIME type, and size before parsing.
- Accept only PDF and DOCX for the prototype.
- Generate server-side file names; never trust an uploaded path or file name.
- Prevent path traversal and archive extraction.
- Keep provider credentials server-side and out of logs, APIs, and frontend bundles.
- Never persist hosted-demo admin-entered provider credentials to SQLite; keep them in process memory only and clear them on restart. Use an approved enterprise secret manager in the on-premises target.
- Redact secrets and document contents from application logs.
  **P6 status:** `backend/app/core/job_runner.py`'s blanket exception handler logs the
  exception type and review_id only, never the message/traceback — closed a real gap where a
  `ModelOutputInvalidError` could echo quoted document evidence text into logs. Verified with
  a test forcing a failure carrying fake secret/evidence sentinels and asserting they never
  appear in captured logs. See `docs/SECURITY_EVIDENCE.md` section 3.
- Apply request-size limits, timeouts, and rate limits.
  **P6 status:** upload size is enforced twice — an early `Content-Length`-based rejection
  (`MaxBodySizeMiddleware`) plus the original post-read check in `upload.py`, which stays
  authoritative since `Content-Length` can be omitted or wrong. Per-service HTTP timeouts
  already existed (Ollama, Qdrant, embedding calls). Rate limiting is explicitly not
  implemented — meaningless to scope correctly without an auth/identity layer; deferred to
  P7 alongside real authentication.
- Require authenticated access to the hosted portal and admin authorization for configuration operations.
  **P7 status:** implemented for the hosted portal — `DemoBasicAuthMiddleware`
  (`backend/app/core/middleware.py`) gates every request behind HTTP Basic
  Auth whenever `deployment_mode: demo`, failing closed if credentials are
  unconfigured (D-06). Admin authorization specifically: `PUT /config` is
  additionally, unconditionally locked in demo mode regardless of the
  Basic Auth gate, since the hosted demo offers nothing to configure
  (deterministic-only, D-05 stays open). `PUT /config` remains
  unauthenticated in **local** mode by design — this is a single-operator
  local dev/PoC assumption, disclosed, not silently gapped.
- Restrict CORS to the deployed frontend origin.
  **P7 status:** the hosted demo serves frontend and backend same-origin
  from one container (see ADR-012), which removes the cross-origin case for
  the hosted deployment entirely — no CORS allowlist entry needed there.
  Local dev CORS behavior is unchanged since P0/P6
  (`backend/tests/test_cors.py`).
- Use TLS at the public ingress.
  **P7 status:** Render is expected to provide TLS automatically at its ingress once the
  hosted demo is deployed. This has **not been live-verified** — the actual public
  deployment is deferred to a later polish/optimization phase (not a P7 blocker), so no
  request has yet been made against a real hosted TLS endpoint. Local dev remains plain HTTP
  by design (no public ingress exists there).
- Delete temporary uploaded files after processing according to the configured retention policy.
  Unchanged since P1, re-confirmed live in P6 (`docs/SECURITY_EVIDENCE.md` section 9). As of
  P6, review *records* (not just temp files) also expire per the Retention Defaults below —
  see the note there.
- Validate configurable model endpoints against provider, scheme, hostname, resolved IP range, and egress policy.
  **P6 status:** `backend/app/services/ssrf_guard.py` implements this as a blocklist-first
  check — always blocks link-local/metadata/reserved/multicast; private RFC1918 ranges
  allowed only in local mode; fixed hostnames (`localhost`, `127.0.0.1`, `ollama`) always
  allowed. This is not a full enterprise egress-policy allowlist — see
  `docs/SECURITY_EVIDENCE.md` section 1's stated limitation.
- Never load Haystack pipeline definitions, snapshots, prompts, or Python callables from user input.
  **P3 compliance:** `backend/app/services/haystack_pipeline.py`'s components and the
  `AsyncPipeline` assembled in `clause_intelligence.py` are constructed entirely in Python
  code, built lazily on first use (not at module import time, so app startup never depends
  on Ollama being reachable), and never deserialized from configuration, a file, or a
  request. Prompts (`ollama_adapter.py`) are fixed constants matching `PROMPT_SPEC.md`
  verbatim, not runtime-configurable.
- **P3 addition:** `haystack-ai` pulls in `posthog` (telemetry) as a transitive dependency.
  Disabled via `HAYSTACK_TELEMETRY_ENABLED=False`, set unconditionally in
  `backend/app/__init__.py` (before `haystack` is imported anywhere) and redundantly in
  `docker-compose.yml`.
- Bind Qdrant privately and enable authentication; do not expose its ports publicly.
  **P4 status:** the `qdrant` Compose service (opt-in, `retrieval` profile) publishes no host
  port at all — tighter than the Ollama services' setup — so it is unreachable from outside
  the Compose network by construction.
  **P6 status:** API-key authentication is now implemented and optional
  (`Settings.qdrant_api_key`, threaded through `GuidanceService`, the health check, and
  `scripts/index_guidance.py`). Unset by default (Qdrant's own unauthenticated default,
  matching the degraded-when-absent design of the whole retrieval feature). Live testing
  found that an *empty-string* key makes Qdrant enforce auth instead of staying unset, so
  `docker-compose.yml` deliberately omits the env var rather than defaulting it to empty —
  enabling real auth requires a `docker-compose.override.yml`, documented in `.env.example`.
  See `docs/SECURITY_EVIDENCE.md` section 5 for the full tested behavior.
- Disable framework telemetry and external model/artifact downloads in local runtime mode.
- Pin dependencies and run dependency/license scanning before release.
- Run services as non-root with minimum filesystem and network permissions.

## On-Premises Target Controls
- Deny outbound internet access by default.
- Use internally managed identity, TLS, secrets, and audit logging.
- Encrypt data at rest and in transit.
- Separate application, model, and data services by network policy.
- Preserve review events and configuration changes in an audit trail.

## Prototype Threat Checklist
- Malicious document or parser exploit
- Prompt injection embedded in contract text
- Model output that violates the schema
- Secret leakage through UI, logs, or error messages
- Unauthorized access to uploaded documents or results
- Server-side request forgery through configurable model endpoints
- Unintended external network calls from dependencies
- Denial of service through large or complex uploads

## Mitigation Principle
Contract text is untrusted data, not an instruction source. Prompts must delimit document content, tools are not exposed to the model, model output is schema-validated, and application rules make the final workflow decisions.

## Retention Defaults
- Hosted Demo mode: original upload deleted immediately after processing; review result expires after 24 hours.
- Local development: seven days unless changed.
- Target enterprise: client policy, legal hold, and records schedule take precedence.

**P6 implementation note:** review-record expiry (not just temp-file cleanup, which was
already implemented since P1) is now enforced via lazy delete-on-read
(`GET /reviews/{id}` returns `REVIEW_EXPIRED` and deletes the row once past
`Settings.retention_hours_local`/`retention_hours_demo`, matching the defaults above). This
is explicitly **PoC-scale retention, not a production records archival policy** — there is
no background sweep, so a review that is never read again after expiring simply stays in
SQLite indefinitely. See `docs/SECURITY_EVIDENCE.md` section 4.

**P7 hosted-demo note:** on the default (free) Render plan, SQLite additionally sits on
ephemeral container storage — every review record is lost on restart/redeploy, independent
of the 24-hour retention logic above. This is a disclosed demo-only exception (see
`docs/OPEN_DECISIONS.md` D-07 and `docs/SECURITY_EVIDENCE.md` section 10), not how the
production on-prem target persists data.

**P8.1 dashboard/history note:** the retention check moved from a `routes_reviews.py`-local
helper into `app/services/retention.py` so `GET /api/v1/reviews` (dashboard/history) and
`GET /api/v1/reviews/{review_id}` enforce identical lazy delete-on-read behavior — same
windows, same "in-progress reviews never expire" rule, no new policy. The list endpoint
deletes any expired terminal review it encounters on a page and excludes it from the
response, so a dashboard/history view never surfaces a review past its retention window,
and a returned page may contain fewer than the requested `limit` when this happens.

## Security Evidence Required Before Deployment
- dependency and container vulnerability scan (not done — still open, out of P7 scope)
- license report and SBOM (not done — still open, out of P7 scope)
- secret scan (not done — still open, out of P7 scope)
- upload validation tests (done since P1; see `docs/SECURITY_EVIDENCE.md` section 2)
- prompt-injection fixture test (done since P2)
- SSRF endpoint tests (done — P6, `docs/SECURITY_EVIDENCE.md` section 1)
- Qdrant network/authentication check (done — P4 network isolation, P6 optional auth; `docs/SECURITY_EVIDENCE.md` section 5)
- egress observation in local mode (done — P3 model-path egress-blocked run, P6 default-path egress-blocked run; `docs/SECURITY_EVIDENCE.md` section 7)
- hosted-demo access control, config lock, and deployment-shape check (done — P7, `docs/SECURITY_EVIDENCE.md` section 10)

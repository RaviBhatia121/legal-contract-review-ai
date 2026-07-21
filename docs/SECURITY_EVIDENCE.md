# Part 2 Security Evidence (P6-P7)

Factual record of the security controls added or verified in P6 and P7. Each
entry states the command run, the result observed, the date, and the known
limitation — no marketing language, no unverified claims. This is prototype
(PoC) evidence, not a production security audit or penetration test.

## 1. SSRF hardening — Ollama `base_url`

**Control:** `backend/app/services/ssrf_guard.py`, wired into `PUT /api/v1/config`.
Blocklist-first: always blocks link-local/metadata/reserved/multicast/unspecified
ranges; allows private RFC1918 ranges only in `deployment_mode: local`; always
allows `localhost`, `127.0.0.1`, and the Docker Compose hostname `ollama`.

| Test | Command/input | Result | Date |
|---|---|---|---|
| Cloud metadata address rejected | `PUT /config {"base_url":"http://169.254.169.254/"}` (local and demo mode) | `400 CONFIGURATION_INVALID`, "link-local" | 2026-07-19 |
| Multicast rejected | `PUT /config {"base_url":"http://224.0.0.1:11434"}` | `400 CONFIGURATION_INVALID`, "multicast" | 2026-07-19 |
| Reserved range rejected | `PUT /config {"base_url":"http://240.0.0.1:11434"}` | `400 CONFIGURATION_INVALID`, "reserved" | 2026-07-19 |
| Private range allowed in local mode | `PUT /config {"base_url":"http://192.168.1.50:11434"}`, `deployment_mode: local` | `200 OK` | 2026-07-19 |
| Private range rejected in demo mode | Same input, `deployment_mode: demo` | `400 CONFIGURATION_INVALID`, "only permitted in local deployment mode" | 2026-07-19 |
| Docker service hostname allowed | `PUT /config {"base_url":"http://ollama:11434"}` | `200 OK` | 2026-07-19 |
| Unresolvable hostname rejected | `PUT /config {"base_url":"http://this-host-does-not-exist.invalid/"}` | `400 CONFIGURATION_INVALID`, "could not be resolved" | 2026-07-19 |
| Invalid scheme rejected | `PUT /config {"base_url":"javascript:alert(1)"}` | `400 CONFIGURATION_INVALID` | 2026-07-19 |
| Public address allowed | `PUT /config {"base_url":"http://8.8.8.8:11434"}` | `200 OK` | 2026-07-19 |

Full automated coverage: `backend/tests/test_ssrf_guard.py` (12 tests, run as
part of `python -m pytest -q`).

**Limitation:** this blocks specific known-dangerous ranges; it is not a
strict default-deny allowlist or a full enterprise egress policy. A public
IP is allowed by default. DNS rebinding between validation time and request
time is not specifically defended against (out of scope for a PoC — the
admin submitting the URL is already a trusted operator in local mode).

## 2. Upload size limits (defense in depth)

**Control:** two independent layers — `MaxBodySizeMiddleware`
(`backend/app/core/middleware.py`) rejects based on the client-supplied
`Content-Length` header before the body is read; `validate_and_read_upload`
(`backend/app/services/upload.py`, unchanged since P1) rejects based on the
actual bytes read, regardless of what `Content-Length` claimed.

| Test | Command/input | Result | Date |
|---|---|---|---|
| Early rejection (oversized `Content-Length`) | 20MiB raw body to `POST /reviews`, threshold 16MiB | `413`, `FILE_TOO_LARGE`, request never reached upload parsing | 2026-07-19 |
| Post-read rejection still active | 15MiB+11 byte PDF, under the middleware's 16MiB threshold | `400`, `FILE_TOO_LARGE` from `validate_and_read_upload` | 2026-07-19 |
| Normal small request unaffected | `GET /health/live` | `200 OK` | 2026-07-19 |

Automated coverage: `backend/tests/test_middleware.py` (2 tests) plus the
pre-existing `test_reviews_golden_path.py::test_upload_rejects_oversized_file`.

**Limitation:** the middleware only catches requests that declare an
oversized `Content-Length`; a client that omits it or streams chunked data
without one bypasses the early check and relies entirely on the post-read
check — this is documented and intentional (item 2 in the approved plan:
"middleware is early rejection, not the only protection").

## 3. Log redaction

**Control:** `job_runner.py`'s blanket exception handler logs
`type(exc).__name__` and `review_id` only — never the exception message or
traceback, which could otherwise echo quoted document evidence text (e.g.
from a `ModelOutputInvalidError`).

| Test | Method | Result | Date |
|---|---|---|---|
| Secret/evidence sentinel never logged | Forced an internal failure with a `RuntimeError` embedding a fake credential and fake evidence text; captured logs via `caplog` | Sentinels absent from `caplog.text`; log line contained only `RuntimeError` and the review UUID | 2026-07-19 |
| Sentinel never in API response | Same run, inspected `GET /reviews/{id}` | Sentinels absent from response body; only the fixed generic `INTERNAL_ERROR` message returned | 2026-07-19 |

Automated coverage: `backend/tests/test_log_redaction.py` (1 test).

**Limitation:** this is a single blanket handler; it does not exhaustively
guarantee no other code path could log something (only two log call sites
exist in the entire backend as of this audit — both reviewed).

## 4. Retention — PoC delete-on-read, not production archival

**Control:** `_is_expired`/lazy delete in `backend/app/api/routes_reviews.py`.
A completed/failed review past its retention window is deleted the next
time `GET /reviews/{id}` is called for it, returning `REVIEW_EXPIRED` (410).
Defaults: 7 days local mode, 24 hours demo mode
(`Settings.retention_hours_local`/`retention_hours_demo`).

**This is explicitly PoC-scale retention, not a production records
archival policy:** there is no background sweep — an expired review that is
never read again simply stays in SQLite indefinitely. It provides no legal
hold, audit trail, or guaranteed deletion SLA. Production/enterprise use
requires real archival tooling per `SECURITY_AND_DATA.md`'s "Target
enterprise: client policy, legal hold, and records schedule take
precedence."

| Test | Method | Result | Date |
|---|---|---|---|
| Fresh review not expired | Complete a review, `GET` immediately | `200 OK` | 2026-07-19 |
| Expired review returns 410 and is deleted | Age `completed_at` past `retention_hours_local`, then `GET` | `410 REVIEW_EXPIRED`; second `GET` → `404 REVIEW_NOT_FOUND` (row actually gone) | 2026-07-19 |
| Within-window review not expired | Age just under the window | `200 OK` | 2026-07-19 |
| Demo mode uses shorter window | Set `deployment_mode: demo`, age past the 24h window (but under the 7-day local window) | `410 REVIEW_EXPIRED` | 2026-07-19 |
| In-progress review never expires | Age `created_at` by 365 days on a non-terminal review | Still returns its live status, not `REVIEW_EXPIRED` | 2026-07-19 |

Automated coverage: `backend/tests/test_retention.py` (5 tests).

## 5. Qdrant authentication — optional, degraded when unset

**Control:** `Settings.qdrant_api_key` (env `PART2_QDRANT_API_KEY`), threaded
through `GuidanceService`, `check_qdrant_reachable`, and
`scripts/index_guidance.py` via `qdrant_client.AsyncQdrantClient(api_key=...)`.
`None`/unset → unauthenticated (Qdrant's own default); a real value →
authenticated. No host port is published for the `qdrant` Compose service
(unchanged since P4).

**Important finding from live testing:** setting
`QDRANT__SERVICE__API_KEY` to an *empty string* on the Qdrant container
does **not** behave the same as leaving it unset — Qdrant treats an empty
string as "a key is configured" and starts rejecting unauthenticated
requests. Because of this, `docker-compose.yml` does **not** set that env
var by default (a naive `${QDRANT_API_KEY:-}` default would have silently
broken the unauthenticated default state). Enabling auth requires a
`docker-compose.override.yml` — see `.env.example`.

| Test | Method | Result | Date |
|---|---|---|---|
| Empty-string key breaks default state (why the override-file approach was chosen) | `docker run ... -e QDRANT__SERVICE__API_KEY=""`, unauthenticated `get_collections()` | `401 Unauthorized` — confirmed empty string ≠ unset | 2026-07-19 |
| Default (no env var) stays unauthenticated | Standard `docker compose --profile retrieval up -d qdrant`, unauthenticated request | `200 OK` (list of collections returned) | 2026-07-19 |
| Real key enforces auth | `docker run ... -e QDRANT__SERVICE__API_KEY=test-secret-key`, request without a key | `401 Unauthorized` | 2026-07-19 |
| Real key with matching client key succeeds | Same container, `AsyncQdrantClient(api_key="test-secret-key")` | `200 OK` | 2026-07-19 |
| `PART2_QDRANT_API_KEY=""` normalizes to unauthenticated | `Settings(qdrant_api_key="")` via env | `settings.qdrant_api_key is None` | 2026-07-19 |

Automated coverage: `backend/tests/test_qdrant_auth.py` (6 tests).

**Limitation:** no TLS on the Qdrant connection (plaintext, matches
`SECURITY_AND_DATA.md`'s target-enterprise gap); the API key itself has no
rotation mechanism and is a Compose-managed secret with the same
"no enterprise secret manager yet" limitation as model credentials.

## 6. CORS

**Control:** unchanged since P0 — `CORSMiddleware` restricted to
`Settings.cors_allow_origins`. P6 adds explicit test evidence.

| Test | Command | Result | Date |
|---|---|---|---|
| Disallowed origin gets no CORS header | `GET /health/live` with `Origin: https://evil.example.com` | `200 OK`, no `Access-Control-Allow-Origin` header | 2026-07-19 |
| Allowed origin gets CORS header | Same request with `Origin: http://localhost:5173` | `200 OK`, `Access-Control-Allow-Origin: http://localhost:5173` | 2026-07-19 |

Automated coverage: `backend/tests/test_cors.py` (2 tests).

## 7. Egress-blocked / local-only verification

**Control/claim:** the default deterministic review path (no Ollama, no
Qdrant) requires zero outbound network access.

**Method:** recreated the Compose network with `internal: true` (temporary
override, not committed), backend-only, no `ollama`/`qdrant` services
running. Confirmed egress genuinely blocked (`urllib` → `Network is
unreachable` against `1.1.1.1`) before, during, and after the run. Drove
the API from inside the backend container (no host port with `internal:
true`). Uploaded `fixtures/sentinel-support-agreement.pdf` via the real
API and diffed the result against an identical run with normal networking.

| Check | Result | Date |
|---|---|---|
| Egress blocked before run | `Network is unreachable` | 2026-07-19 |
| Golden fixture completes | `status: completed`, `overall_risk: Critical` | 2026-07-19 |
| Egress still blocked after run | `Network is unreachable` | 2026-07-19 |
| Result identical to normal-networking baseline | Byte-for-byte identical (excluding `review_id`/`finding_id`/`completed_at`) | 2026-07-19 |

**Note:** this is distinct from and does not duplicate P3's egress-blocked
verification, which specifically proved the Ollama+model path works with
egress blocked (Ollama itself running, only external internet blocked).
This P6 check proves the separate claim that the *default* path needs no
Ollama/Qdrant/internet at all.

## 8. Port and service inventory

| Service | Host port published? | Profile |
|---|---|---|
| backend | Yes, `8420` (unchanged) | default |
| frontend | Yes, `5420` (unchanged) | default |
| ollama | No by default; optional `11434` only if `--profile local-model` is used | `local-model` (opt-in) |
| qdrant | No | `retrieval` (opt-in) |

Current shared-VM follow-up behavior: default `docker compose up` starts only `backend`
and `frontend`; model-assisted review calls the shared on-prem Ollama VM
(`http://<ollama-vm-ip>:11434`, `qwen3.6:35b`). The laptop-local Ollama service is retained
only as an opt-in fallback profile and is not running in the accepted local demo state.
Other locally running Docker projects
(`ai-boardroom-*`, `omniflow-*`) confirmed unaffected throughout all P6
work (container uptime unchanged before/after).

## 9. Temporary upload cleanup

Unchanged since P1, re-confirmed in P6: ran a review to completion, then
inspected the container's upload-temp directory.

| Check | Result | Date |
|---|---|---|
| `upload_tmp/` after a completed review | Directory exists (created on demand), contents empty | 2026-07-19 |

## What P6 does NOT cover (explicitly out of scope)

- Authentication/authorization on any endpoint in local mode.
- TLS anywhere in the stack.
- Rate limiting.
- Full enterprise secret manager, SBOM/license scan, container
  vulnerability scan — these are `SECURITY_AND_DATA.md`'s pre-deployment
  (P7) evidence list, not P6.
- Full DNS-rebinding-resistant or allowlist-only SSRF protection.

See `RISK_REGISTER.md` for how each risk's status changed and
`IMPLEMENTATION_PHASE_PLAN.md` P6 Completion Notes for the full narrative.

## 10. Hosted demo (P7) — access control, config lock, and deployment shape

**Controls:**
- `DemoBasicAuthMiddleware` (`backend/app/core/middleware.py`) gates every
  request behind HTTP Basic Auth whenever `Settings.deployment_mode ==
  "demo"`, using `Settings.demo_access_username`/`demo_access_password`
  (env vars `PART2_DEMO_ACCESS_USERNAME`/`PART2_DEMO_ACCESS_PASSWORD`, set
  only on the hosted platform, never committed). Fails closed — if demo mode
  is active but credentials are unset, every request is rejected rather than
  served unauthenticated. `/api/v1/health/live` is exempt so the hosting
  platform's own process check is not credential-gated.
- `PUT /api/v1/config` unconditionally rejects with `CONFIGURATION_INVALID`
  when `deployment_mode == "demo"`, regardless of payload — a backend lock,
  not just a hidden admin nav link in the frontend (`backend/app/api/
  routes_config.py`).
- The hosted demo is deterministic-only: no `PART2_PROVIDER_TYPE`,
  `PART2_OLLAMA_BASE_URL`, or `PART2_QDRANT_URL` are set in `render.yaml` —
  there is no model provider or vector store reachable from the hosted
  environment (D-05 stays open).
- Frontend and backend are served same-origin from one container
  (`backend/Dockerfile.hosted` builds the frontend, copies `dist/` into
  `/app/static`, and `app/main.py`'s SPA fallback route serves it), so the
  hosted deployment has no cross-origin case to defend and needs no CORS
  allowlist entry for its own UI.

All of the following were run against the image built from
`backend/Dockerfile.hosted`, run locally with `docker run`. This is accepted
as sufficient evidence for P7: the actual live Render deployment is
**explicitly deferred to a later polish/optimization phase**, by decision —
not a P7 exit-criteria gap. Live-URL evidence is added once that later phase
runs the deploy, per `docs/DEMO_RUNBOOK.md`.

| Test | Command | Result | Date |
|---|---|---|---|
| Liveness reachable without credentials | `curl /api/v1/health/live` | `200 OK` | 2026-07-19 |
| Config unreachable without credentials | `curl /api/v1/config` | `401`, `WWW-Authenticate: Basic` | 2026-07-19 |
| Config reachable with correct credentials | `curl -u demo:change-me /api/v1/config` | `200 OK`, `"deployment_mode":"demo","synthetic_data_only":true` | 2026-07-19 |
| Config writes rejected even when authenticated | `curl -u demo:change-me -X PUT /api/v1/config -d '{"model_name":"x"}'` | `400 CONFIGURATION_INVALID`, "Configuration changes are disabled in hosted demo mode." | 2026-07-19 |
| Frontend served same-origin at `/` | `curl -u demo:change-me /` | `200 OK`, `text/html` | 2026-07-19 |
| Client-side route resolves on hard refresh | `curl -u demo:change-me /reviews/abc` | `200 OK`, `index.html` fallback served | 2026-07-19 |
| Default local docker-compose stack unaffected | `docker compose up -d --build backend`, `curl /api/v1/health/ready` and `curl /api/v1/config` (no `PART2_DEPLOYMENT_MODE=demo` set) | `200 OK` on both, no auth required — confirms the demo gate is a true no-op in local mode | 2026-07-19 |
| Local ports unchanged | `docker compose config` | `8420`/`5420` published, matching pre-P7 | 2026-07-19 |

Automated coverage: `backend/tests/test_demo_access.py` (6 tests),
`backend/tests/test_health.py::test_update_config_rejected_unconditionally_in_demo_mode`,
`frontend/tests/demo-mode.test.tsx` (2 tests — admin nav hidden and demo
banner/on-prem disclaimer shown only in demo mode).

**Persistence — explicit demo-only exception:** the default `render.yaml`
configuration uses Render's free Web Service plan, which does not support a
persistent disk. SQLite therefore lives on the container's ephemeral
filesystem: every review record is lost on restart, redeploy, or platform
instance recycling. This is disclosed, not silently accepted as
production-equivalent — it is acceptable here because the hosted demo only
ever holds synthetic data with a 24-hour retention window regardless
(`Settings.retention_hours_demo`), and it is explicitly not how the
production on-prem target persists data. A paid Render plan with a mounted
disk (or Render Postgres) is the documented upgrade path in `render.yaml`
if hosted persistence is ever needed; it was not adopted for this PoC.

**Limitation:** Basic Auth is a presentation-access control (satisfies D-06
at the "simple authenticated app session" level only), not a real
user-identity or audit-trail system. Rate limiting remains unimplemented —
the small expected audience plus the Basic Auth gate is the accepted
mitigation for a demo, not a substitute for real rate limiting. TLS at the
hosted ingress is *expected* to be provided automatically by the platform
(Render terminates TLS by default) once the hosted demo is actually
deployed — this has **not been live-verified**, since the public deployment
itself is deferred to a later polish/optimization phase (not a P7 blocker).
Local dev remains plain HTTP by design.

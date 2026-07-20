# Part 2 - Legal Contract Risk Review

Prototype intranet portal for structured, non-chat Legal contract risk review. Start with
[docs/MASTER_INDEX.md](./docs/MASTER_INDEX.md) for the full specification pack.

## Current Phase: P7 Hosted Demo and Polish (complete)

**Hosted demo URL:** `TBD` — packaging is complete, accepted, and verified locally (see
below). Going live on Render is **explicitly deferred to a later polish/optimization
phase**, by decision — not a gap in P7. This hosted URL, once live, will be a **synthetic
demo convenience only** — it is not the target production architecture. The production
deployment target is fully on-premises (Docker-based Ollama/Qdrant, no cloud calls); see
`docs/ARCHITECTURE_DECISIONS.md` ADR-012.

P0-P7 are complete. P3 adds real, general (not fixture-tuned) clause classification and
attribute extraction via a provider-neutral model adapter (`backend/app/model_adapter/`,
only Ollama implemented) orchestrated with a lazily-built Haystack `AsyncPipeline`
(`backend/app/services/haystack_pipeline.py`). The deterministic rule engine
(`backend/app/services/rule_engine.py`) remains the unchanged, sole source of truth for risk
decisions regardless of which extraction path fed it. `clause_intelligence_mode` defaults to
`deterministic` everywhere, including Docker Compose; model mode is strictly opt-in via
`PART2_CLAUSE_INTELLIGENCE_MODE=model` plus `docker compose --profile local-model up`. The
PoC validation model is Docker-hosted Ollama with `qwen3:4b` so the demo proves the workflow
without requiring a heavy local model; stronger local models can be tested later if quality
is insufficient. P3 is live-verified: 3 runs plus 1 egress-blocked run of the golden fixture
against real Docker Ollama + `qwen3:4b` produced identical rule IDs, severities, missing
clauses, overall risk, and confidence values — see `docs/IMPLEMENTATION_PHASE_PLAN.md` P3
Live Verification Notes and `docs/TEST_AND_ACCEPTANCE_PLAN.md` Repeatability Tests. Note:
`qwen3:4b` did not classify some clause types present in the fixture text (a disclosed
model-quality limitation, see `docs/RISK_REGISTER.md` R-03), and the live-model results
diverge from P2's deterministic fixture-tuned numbers by design — these are two different,
independently correct extraction paths feeding the same unchanged rule engine.

P4 adds supplemental guidance retrieval: every finding can carry a `guidance` list of
illustrative negotiation tips, approved-example language, or playbook cross-references,
retrieved from Qdrant strictly *after* rule evaluation (`backend/app/services/
guidance_retrieval.py`; `rule_engine.py` is not modified by P4 and is never called by
retrieval code). Query embeddings are computed locally via Docker Ollama
(`qllama/multilingual-e5-small`, a GGUF quantization of the MIT-licensed
`intfloat/multilingual-e5-small`). Retrieval is opt-in via `docker compose --profile
retrieval up` and always degrades cleanly (`retrieval_mode: degraded_full_rules`,
`guidance: []` on every finding, review still completes) when Qdrant or the embedding model
is unreachable — verified live: a direct diff of retrieval-on vs retrieval-off API responses
for the same golden-fixture document showed identical rule IDs, severities, missing clauses,
and overall risk. See `docs/IMPLEMENTATION_PHASE_PLAN.md` P4 Completion Notes.

**Schema-change note:** P4 added `Finding.guidance_json`. There is no migration tooling in
this prototype — if you have an existing local SQLite volume from before P4, run
`docker compose down -v` before bringing the stack back up, or the backend will fail against
the stale schema. P5, P6, and P7 made no schema changes.

P5 makes `/admin/model` a real editable config screen instead of a read-only display:
provider select, model name, Ollama base URL, a write-only credential field, Save, and Test
connection with a live success/failure + latency result. Only `ollama` can actually be saved
as active config (`PUT /config` rejects any other `provider_type` with `CONFIGURATION_INVALID`
— not silently ignored); Anthropic/OpenAI/Gemini are shown in the catalog
(`GET /api/v1/config/providers`) as disabled "(Not enabled)" options to demonstrate provider
portability via the UI/interface only. **No real cloud adapter was implemented — D-05
(hosted demo model provider) remains open.** `base_url` is rejected outright for any
non-Ollama provider or if it isn't a valid `http://`/`https://` URL with a hostname.
Live-verified in the browser and via `curl` against the running Docker stack — see
`docs/IMPLEMENTATION_PHASE_PLAN.md` P5 Completion Notes.

P6 adds practical security hardening for a defense-sector/on-prem case study, without
overbuilding for a 2-day PoC. SSRF: `backend/app/services/ssrf_guard.py` DNS-resolves the
Ollama `base_url` and always blocks link-local/metadata (incl. `169.254.169.254` cloud
metadata)/reserved/multicast/unspecified addresses; private RFC1918 ranges are allowed only
in `local` deployment mode (rejected in demo mode); `localhost`, `127.0.0.1`, and the Docker
Compose hostname `ollama` are always allowed. Upload size is now enforced twice — an early
`Content-Length`-based rejection (`MaxBodySizeMiddleware`) plus the original post-read check,
which stays authoritative since `Content-Length` can be omitted or wrong. Log redaction:
`job_runner.py`'s exception handler logs only the exception type and review_id, never the
message/traceback, closing a real gap where quoted document evidence could leak into logs.
Retention: completed/failed reviews now expire (lazy delete-on-read, `410 REVIEW_EXPIRED`
then `404` on a later read) per `Settings.retention_hours_local`/`retention_hours_demo` —
explicitly PoC-scale retention, not production records archival. Qdrant authentication is
now optional and wired consistently through retrieval, the health check, and
`scripts/index_guidance.py` (`Settings.qdrant_api_key`, unset = Qdrant's own unauthenticated
default); live testing found and fixed a real bug where an *empty-string* key makes Qdrant
wrongly enforce auth, so `docker-compose.yml` deliberately omits the env var rather than
defaulting it to empty. CORS and the exposed-port inventory were reviewed and evidenced; an
egress-blocked verification confirms the default deterministic path makes no external calls.
All of this is captured as factual command/result/date/limitation evidence in
`docs/SECURITY_EVIDENCE.md` — see `docs/IMPLEMENTATION_PHASE_PLAN.md` P6 Completion Notes for
the full corrections list. P6 deliberately does not implement admin authentication, TLS, or
rate limiting (no hosted deployment exists yet at that point — that's P7 scope).

P7 packages a shareable hosted demo without weakening the on-prem architecture claim. The
hosted demo is **deterministic-only** — no model provider, Ollama, or Qdrant runs there, so
D-05 (hosted model provider) stays deliberately open rather than being forced by hosting
needs. D-07 (hosting platform) is accepted as Render, Docker Web Service
(`render.yaml`, `backend/Dockerfile.hosted`); persistence on the default free plan is
**ephemeral SQLite** (no persistent disk on that tier) — a disclosed demo-only exception, not
production-equivalent, with a documented paid-plan upgrade path not adopted for this PoC.
Frontend and backend are served **same-origin** from one container (the hosted Dockerfile
builds the frontend and the backend serves its static output via a SPA-fallback route in
`app/main.py`), so there is no cross-origin surface to defend for the hosted UI itself. A new
`DemoBasicAuthMiddleware` (`backend/app/core/middleware.py`) gates every request behind HTTP
Basic Auth whenever `deployment_mode: demo`, failing closed if credentials are unconfigured;
`/health/live` stays exempt for the platform's own process check. `PUT /config` is
additionally, unconditionally locked in demo mode at the backend — not just hidden from the
admin nav — since the hosted demo has nothing to configure. A persistent, non-dismissible
banner states both the synthetic-data warning and the case-study narrative: **this hosted
URL is a synthetic demo convenience, not the production on-prem deployment target.** All of
this was built and verified against the hosted image run locally with `docker build`/`docker
run` — see `docs/SECURITY_EVIDENCE.md` section 10. Actually deploying it to a live Render
URL is **explicitly deferred to a later polish/optimization phase**, by decision, and is not
part of P7's acceptance; `render.yaml` and `backend/Dockerfile.hosted` are ready for that
later phase, and `docs/DEMO_RUNBOOK.md` documents exactly what to fill in once it runs.

The app parses uploaded PDF/DOCX locally (`pypdf`/`python-docx` — Docling was spiked and
rejected for requiring a network model download even with OCR disabled; see
`docs/TECH_STACK_AND_LICENSES.md`) and rejects unsupported, oversized, encrypted, empty, and
out-of-scope files with typed errors.

Fixtures live under `fixtures/`. The original golden fixture is generated by
`scripts/generate_fixtures.py`; additional manual-test contracts are generated by
`scripts/generate_additional_test_contracts.py` (`pip install -e ".[fixtures]"` first).

## Run locally without Docker

### Backend
```
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

### Frontend
```
cd frontend
npm install
npm run dev
```
The Vite dev server proxies `/api/*` to `http://127.0.0.1:8000` (see `frontend/vite.config.ts`).
Open http://localhost:5173.

## Run with Docker Compose
```
docker compose up --build
```
Backend: http://localhost:8420, Frontend: http://localhost:5420.

Health endpoints:
- Backend live: http://localhost:8420/api/v1/health/live
- Backend ready: http://localhost:8420/api/v1/health/ready

Default host ports (8420/5420) deliberately avoid the common 8000/5173 dev-server ports
so this stack does not collide with other locally running projects. Override with
`BACKEND_PORT` / `FRONTEND_PORT` (see `.env.example`) if those are also taken.

The Compose project is explicitly named `legal-contract-review-ai` (`docker-compose.yml`'s
top-level `name:`), so `docker compose ls`/`docker ps` never show it as "Part 2" and it
can't collide with other locally running Compose projects (e.g. `ai-boardroom-*`,
`omniflow-*`). `backend` and `frontend` run with `restart: unless-stopped`, so once started
they come back automatically if Docker restarts (e.g. after a host reboot), without needing
`docker compose up` to be re-run manually — `docker compose down` still stops and removes
them normally. `ollama` and `qdrant` remain opt-in only, with no restart policy, so enabling
either profile once doesn't cause a multi-GB model container to silently reappear on every
reboot.

### Optional local model verification
Use Docker-based Ollama for the PoC so the model runtime is isolated and removable:
```
docker compose --profile local-model up -d ollama
docker compose exec ollama ollama pull qwen3:4b
CLAUSE_INTELLIGENCE_MODE=model MODEL_NAME=qwen3:4b docker compose up -d --build backend
```
Remove the PoC model/runtime later with `docker compose down -v` if you no longer need it.

### Optional supplemental-guidance retrieval

Use Docker-based Qdrant plus a local embedding model for the PoC — independent of the
`local-model` profile above (either can run without the other; both share the `ollama`
container when both are enabled):
```
docker compose --profile retrieval up -d ollama qdrant
docker compose exec ollama ollama pull qllama/multilingual-e5-small
docker compose exec backend python scripts/index_guidance.py
docker compose up -d --build backend
```
No Qdrant host port is published (private by construction). Remove the retrieval
runtime/data later with `docker compose down -v` if you no longer need it.

## Hosted demo image (P7)

`backend/Dockerfile.hosted` and `render.yaml` package a **separate, deterministic-only**
image for a hosted demo — see "Current Phase" above for what this does and does not imply.
This does not affect `docker compose up` above in any way (different Dockerfile, never
referenced by `docker-compose.yml`). Build and run it locally to verify before deploying:
```
docker build -f backend/Dockerfile.hosted -t part2-hosted-demo .
docker run --rm -p 8000:8000 \
  -e PART2_DEPLOYMENT_MODE=demo \
  -e PART2_DEMO_ACCESS_USERNAME=demo \
  -e PART2_DEMO_ACCESS_PASSWORD=change-me \
  -e PART2_CORS_ALLOW_ORIGINS='[]' \
  part2-hosted-demo
```
Then visit http://localhost:8000 with Basic Auth `demo`/`change-me`. To actually deploy it,
push this repo to Render (or any Docker-capable host) using `render.yaml`, and set
`PART2_DEMO_ACCESS_USERNAME`/`PART2_DEMO_ACCESS_PASSWORD` as real secrets in the platform
dashboard — never commit them. See `docs/DEMO_RUNBOOK.md` and `docs/SECURITY_EVIDENCE.md`
section 10.

## Tests

Backend:
```
cd backend && source .venv/bin/activate && python -m pytest -q
```

Frontend:
```
cd frontend && npm run test
```

## Layout
See [docs/REPOSITORY_STRATEGY.md](./docs/REPOSITORY_STRATEGY.md) for the full monorepo layout and boundary rules.

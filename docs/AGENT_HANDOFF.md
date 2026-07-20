# Part 2 Agent Handoff

## Start Here
Read `MASTER_INDEX.md` (`docs/MASTER_INDEX.md` from the repo root) and follow its required
read order before changing code or specifications.

## Repository Location
The repository root moved from `Part2/` to `Part2/legal-contract-review-ai/` after P0.
`Part2/` is now only the case-study workspace folder; it is not the repo. Specification
docs live under `docs/` (this file's own directory) instead of the repo root. See
`REPOSITORY_STRATEGY.md` for the current layout. If any instruction or older note refers to
a bare `backend/`, `frontend/`, or `*.md` path at "Part2/", read it as relative to
`legal-contract-review-ai/` instead.

## Current Phase
P0-P7 are complete, including a live Docker Ollama + `qwen3:4b` golden-fixture verification
(P3, 4/4 runs identical, one egress-blocked), a live Qdrant-backed retrieval verification
(P4, retrieval-on vs retrieval-off produced identical rule outcomes), a live admin-config
save/reject/test-connection verification (P5, real browser + curl checks against the running
Docker stack), live security-control verification including a distinct egress-blocked
default-mode run (P6), and hosted-demo packaging verified against the built hosted image run
locally (P7 — demo Basic Auth, backend-locked config, same-origin serving; see
`docs/SECURITY_EVIDENCE.md` section 10). See `IMPLEMENTATION_PHASE_PLAN.md` P3-P7 notes.

**P7 status note:** the actual live public Render URL is **deferred to a later
polish/optimization phase, not a P7 blocker.** All hosted-demo packaging and its local
verification are complete and accepted as-is (`backend/Dockerfile.hosted`, `render.yaml`,
Basic Auth, demo banner, demo-mode config lock, same-origin serving). Do not move to P8 (or
any further work) without explicit direction. D-05 (hosted model provider) remains
deliberately open — the hosted demo is deterministic-only by design.

## Locked Decisions
- Build a thin purpose-built Legal review application.
- Use mature open-source infrastructure components, not a pre-built contract-review app.
- Keep the workflow structured and non-conversational.
- Support a provider-neutral model adapter.
- Treat Docker-based Ollama/local inference as the PoC validation path and local inference as the target enterprise mode.
- A hosted cloud-backed demo is permitted only with synthetic data and an explicit Demo mode label.
- Use one monorepo rooted at `Part2/legal-contract-review-ai/`.
- Keep the design Unicode-safe and Indonesian-ready while using the English golden fixture for MVP acceptance.

## Next Recommended Task
P7 is complete and accepted. Do not start further work without explicit user direction. The
live public Render URL — actually running `render.yaml`/`backend/Dockerfile.hosted` against a
real Render account and capturing the resulting live-URL evidence in
`docs/DEMO_RUNBOOK.md` — is intentionally **deferred to a later polish/optimization phase**,
not treated as unfinished P7 work. When that phase is authorized, it is also where the
security controls explicitly deferred by P6 (rate limiting, full SSRF/egress allowlisting,
SBOM/vulnerability scanning — see `docs/SECURITY_EVIDENCE.md`'s "What P6 does NOT cover")
would need revisiting for a real public deployment; P7 already closed the TLS and
access-restriction gaps for the hosted path specifically.

A real hosted model adapter (Anthropic/OpenAI/Gemini) remains out of scope until D-05 is
explicitly accepted with a named provider — P5 deliberately implemented provider portability
via the admin UI/catalog/interface only, per the approved corrections.

Before any real (non-demo) reliance on the P3 model path: `qwen3:4b` did not classify
`confidentiality`, `ip_ownership`, or flag `security_incident` deviations that are present in
the golden fixture text, even though the deterministic P2 path and the rule engine both
handle them correctly — see `IMPLEMENTATION_PHASE_PLAN.md` P3 Live Verification Notes and
`RISK_REGISTER.md` R-03 for the disclosed quality caveat.

**Schema-change reminder:** P4 added `Finding.guidance_json`. There is no migration tooling
in this prototype — any pre-P4 SQLite volume needs `docker compose down -v` before the new
code will run against it (documented in `IMPLEMENTATION_PHASE_PLAN.md` P4 Completion Notes
and `README.md`). P5, P6, and P7 made no schema changes. Any future schema change should keep
documenting this same reset requirement rather than silently assuming a fresh volume.

**Qdrant auth reminder:** P6 found that setting `QDRANT__SERVICE__API_KEY` to an empty
string makes Qdrant start enforcing auth — the opposite of "unset." `docker-compose.yml`
deliberately omits that env var by default; enabling real Qdrant auth requires a
`docker-compose.override.yml` (see `.env.example` and `docs/SECURITY_EVIDENCE.md` section 5).

Use `IMPLEMENTATION_PHASE_PLAN.md` as the phase contract. P0-P7 are `complete`. The live
public Render URL is tracked there as deferred to a later polish/optimization phase, not as
an open P7 item.

## Handoff Update Rule
At the end of every implementation session, update:
- current phase
- completed work
- next recommended task
- blockers and unresolved decisions
- `PLAN.md` status
- `IMPLEMENTATION_PHASE_PLAN.md` phase status
- any specifications affected by the implementation

## Completed Work
- Requirements and scope documented.
- Defense-sector playbook template documented.
- Workflow, output, API, and UI contracts documented.
- Architecture, deployment modes, security rules, tests, and traceability documented.
- Original case-study PDF revalidated against the scope.
- Stack licenses and material security caveats checked against primary sources.
- Deterministic rule ownership, model boundaries, data model, fixture, risks, and backlog documented.
- Prompt templates, normalized rule predicates, and 48-hour execution sequence documented.
- Full reconciliation audit completed; conflicts found by the audit were corrected and recorded in `RECONCILIATION_AUDIT.md`.
- Final pre-review audit replaced the English-only embedding proposal with multilingual E5 and issued a green signal.
- Independent Claude audit completed; justified High/Medium/metadata corrections were reconciled, including mandatory successful egress-blocked local-model evidence and typed non-applicable-document behavior.
- Claude post-correction re-audit completed; the remaining low-severity fixture confidence looseness was closed by requiring expected classifications `>= 0.80` and zero golden-fixture `needs_review` findings.
- Pre-implementation review gate created.
- Review gate passed with conditions; scaffold-blocking defaults were accepted.
- Implementation phase plan created and the backlog reconciled to P0-P7 after targeted Claude review.
- P0 handoff wording corrected to remove real parsing from the fixed-result phase.
- P0 implemented and verified: FastAPI backend with SQLite repository boundary, bounded
  in-process job runner with restart recovery, `/api/v1/reviews`, `/api/v1/config`, and
  `/api/v1/health` endpoints; React/Vite frontend with upload, status/findings, and
  read-only admin screens; the full `DEMO_FIXTURE_SPEC.md` fixed result wired end to end;
  Docker Compose stack built and run successfully; 7 backend pytest cases and 2 frontend
  Vitest cases pass.
- Workspace reorganized: repository root moved from `Part2/` to
  `Part2/legal-contract-review-ai/`; all spec/planning `*.md` files moved into `docs/`
  (README.md stays at repo root); generated directories (`.venv`, `node_modules`, `dist`,
  `__pycache__`, `.pytest_cache`, `*.egg-info`) were not moved and were regenerated fresh at
  the new location; two stray artifacts (`frontend/src 2/` empty dir, boilerplate
  `frontend/README.md`) were deleted rather than moved; `CASE_STUDY_BASELINE.md`'s PDF
  reference was changed from a relative link to plain text since the source PDF is
  intentionally kept outside the repo. Ports remain 8420/5420. Re-verified with a fresh
  backend/frontend install, full test suite, and `docker compose up --build` from the new
  root before any cleanup of the old `Part2/backend`, `Part2/frontend` shells.
- P1 implemented and verified: Docling was spiked and rejected (unconditional HF Hub model
  download even with OCR disabled and a text-native PDF, confirmed with a poisoned-proxy
  test); `pypdf`/`python-docx` used instead, verified offline. Added
  `backend/app/services/parsing.py` and `applicability.py`, new `Review` columns
  (`upload_temp_path`, `parsed_text`, `parser_name`, `parser_version`, `parse_error_code`),
  server-side temp-file write/persist/cleanup wired through `routes_reviews.py` and
  `job_runner.py`, five new typed error codes wired to real conditions
  (`ENCRYPTED_DOCUMENT`, `DOCUMENT_TOO_LONG`, `DOCUMENT_PARSE_FAILED`,
  `NO_REVIEWABLE_TEXT`, `DOCUMENT_NOT_APPLICABLE` — the last one a documented provisional
  heuristic only). Generated and committed the full fixture set via
  `scripts/generate_fixtures.py` (`reportlab`, build-time-only, `fixtures` extra). 23
  backend tests pass; full docker-compose smoke test with real fixture PDF confirmed real
  `page_count`/`language`/`parser_name` in API output and confirmed temp-file cleanup
  inside the running container. Findings/clauses remain the P0 fixed fixture per the P1
  boundary; P2 replaces them with real rule evaluation.
- P2 implemented and verified per the approved plan and its 4 corrections: (1) canonical
  `clause_type` enum adopted from `DEFENSE_PLAYBOOK_TEMPLATE.md`, replacing P0/P1's ad hoc
  strings; (2) `backend/app/fixtures/fixed_result.py` kept until all P2 tests passed, then
  deleted in this change set along with the now-empty `app/fixtures/` package; (3)
  `DOCUMENT_NOT_APPLICABLE` left untouched as P1's provisional heuristic, explicitly
  deferred to P3; (4) segmentation/extraction docstrings and doc updates state plainly this
  is fixture-oriented deterministic pattern matching, not general contract parsing — grepped
  the frontend for overclaiming language and found none. Added
  `playbooks/defense-services-v1.json` (27-rule playbook, loaded by
  `backend/app/playbook/loader.py`), `backend/app/services/segmentation.py`,
  `attribute_extraction.py`, and `rule_engine.py`. Extended P1's `ParsedDocument` with
  `page_boundaries` so findings get real page attribution without a new persisted column
  (rule evaluation runs synchronously within the same job-runner pass as parsing). Backend
  Docker build context moved from `backend/` to the repo root so the image can include
  `playbooks/`; added a root `.dockerignore`. 68 backend tests pass (45 new, including all
  27 rule predicates individually, the `REV-001` confidence boundary, the `AUD-001`
  dual-purpose missing-vs-deviation behavior, and adversarial-sentence resistance). Golden
  fixture (PDF and DOCX) reproduces the exact 8 expected rule IDs/severities/evidence/pages
  from `fixtures/sentinel-support-agreement.expected.json`. Full docker-compose smoke test
  confirmed the real rule engine runs correctly in the container
  (`model_provider: rule-engine`); other locally running Docker projects unaffected.
- P3 implemented per the approved plan and its 3 corrections: (1) default
  `clause_intelligence_mode` is `deterministic` everywhere, including `docker-compose.yml`
  (model mode requires both an env var and the `local-model` compose profile); (2) the
  Haystack `AsyncPipeline` is built lazily inside `ClauseIntelligenceService`, never at
  import time, so app startup never depends on Ollama; (3) `/config/test` does a real
  backend-only Ollama ping, no admin UI save/edit work (still P5). Added
  `backend/app/model_adapter/` (`base.py` Protocol, `ollama_adapter.py`, `errors.py`, only
  Ollama implemented), `backend/app/services/block_splitter.py` (general, not fixture-tuned),
  `backend/app/services/haystack_pipeline.py` (`ClauseClassifierComponent`,
  `AttributeExtractorComponent`, both needing a sync `run()` stub plus a real `run_async()`
  for Haystack's async pipeline to await them correctly — confirmed by reading Haystack's own
  source after a first attempt with plain `Pipeline`/`run()` silently failed to await),
  `backend/app/services/clause_intelligence.py`, and `backend/app/schemas/model_io.py` +
  `clause_attributes.py`. Refactored (not rewritten) `rule_engine.py`: extracted
  `evaluate_clauses(clause_inputs, playbook, source=...)` as the reusable core behind the new
  source-agnostic `ClauseInput`; all 27 pre-existing predicate tests passed unchanged,
  confirming the refactor preserved behavior. Rewrote `applicability.py`: real
  `is_applicable()` (>= 2 required clause types classified at >= 0.60 confidence) replacing
  the P1 word-count heuristic, run immediately after classification per a disclosed
  `WORKFLOW_SPEC.md` stage-order correction (applicability needs classification output).
  `Finding.source` is `"model_assisted_rule"` for evidence-based model-path findings,
  `"rule"` for the deterministic path and always for missing-clause findings. Disabled
  Haystack's transitive `posthog` telemetry via `HAYSTACK_TELEMETRY_ENABLED=False` set in
  `backend/app/__init__.py` before any `haystack` import. 82 backend tests pass (14 new,
  including `OllamaAdapter` against a stdlib mock HTTP server, `AsyncPipeline` component
  wiring with a fake adapter, and the new `applicability.is_applicable` behavior). Full
  `docker compose up --build` smoke test in default deterministic mode reproduced the exact
  golden-fixture findings and a clean `PROVIDER_UNAVAILABLE` `/config/test` response with no
  Ollama running. **Marked `blocked`, not `complete`:** this environment has no Ollama
  installed, and installing/running one (multi-GB model pull, external binary execution) was
  judged out of scope to do unilaterally — flagged to the user in the approved P3 proposal's
  risk section before implementation began. Everything gate-able without a live model is
  implemented and tested.
- P3 live verification completed with explicit user approval (Docker-based Ollama only, no
  host install): started `docker compose --profile local-model up -d ollama`, pulled
  `qwen3:4b` (2.5GB, ~10 min), rebuilt backend with
  `CLAUSE_INTELLIGENCE_MODE=model MODEL_NAME=qwen3:4b`. First live attempt failed —
  `/api/generate` cannot suppress qwen3:4b's "thinking" behavior (the model's full JSON
  answer landed entirely in Ollama's discarded `thinking` field, leaving `response` empty;
  reproduced directly against the container to confirm root cause). Fixed
  `ollama_adapter.py` to use `/api/chat` with `"think": false` instead of
  `/api/generate` — a genuine adapter-correctness fix for reasoning-capable local models, not
  a scope change. Updated `test_ollama_adapter.py`'s mock envelope to match; all 82 backend
  tests still pass. Also exposed `PART2_OLLAMA_TIMEOUT_S` through `docker-compose.yml`
  (default unchanged at 60s) since real CPU inference (~2-3 min/call on 14 vCPU, no GPU) is
  far slower than the mocked tests. Ran `fixtures/sentinel-support-agreement.pdf` through the
  real API 3 times plus once with genuine Docker network-level egress blocking
  (`internal: true` override, backend+ollama only, frontend stopped; confirmed
  `Network is unreachable` from inside the backend container before/during/after). All 4 runs
  were identical: High risk, 7 findings (DATA-002/LIAB-002/SUB-002/TERM-001/TERM-002), 2
  missing clauses (AUD-001/SEC-004), confidence 0.9 throughout, 0 needs_review,
  `model_provider: ollama`/`model_name: qwen3:4b`, `source: model_assisted_rule` on evidence
  findings and `source: rule` on missing-clause findings. These numbers differ from P2's
  fixed 8-finding/Critical golden result — expected per `TEST_AND_ACCEPTANCE_PLAN.md` (model
  path is judged on 3-run self-consistency, not reproducing the fixture-tuned deterministic
  numbers) — but `qwen3:4b` did not classify confidentiality/IP-ownership clauses present in
  the text, a real, disclosed model-quality limitation (`RISK_REGISTER.md` R-03). Full
  pytest (82 passed) and default-mode docker-compose smoke test (exact 8-rule golden fixture,
  unchanged) reconfirmed after reverting to normal networking. Other local Docker projects
  (`ai-boardroom-*`, `omniflow-*`) unaffected throughout. P3 moved from `blocked` to
  `complete`. Full detail in `IMPLEMENTATION_PHASE_PLAN.md` P3 Live Verification Notes.
- P4 implemented and live-verified per the approved plan and its 4 corrections: (1) Qdrant is
  genuinely queried for every rule (real `query_points` vector search plus a `rule_id`
  payload filter, falling back to an unranked `scroll` if only the embedder is unreachable)
  rather than an in-process JSON lookup; (2) the embedding-model spike was run and documented
  rather than silently swapping models — `qllama/multilingual-e5-small` (a GGUF quantization
  of the already-accepted, MIT-licensed `intfloat/multilingual-e5-small`) was found via
  `WebSearch`, pulled into the existing Docker Ollama container, and verified end to end
  (384-dim, deterministic) before adoption; spike passed, no fallback substitution was
  needed; (3) the frontend never renders the raw `retrieval_mode` enum — it shows
  "Supplemental guidance available" or "Guidance unavailable, rule review unaffected"; (4)
  the new `Finding.guidance_json` column is a genuine schema change with no migration
  tooling, documented as requiring `docker compose down -v` before first use, same as the P2
  precedent. Added `backend/app/playbook/guidance_loader.py`,
  `backend/app/services/embedding_client.py`, `backend/app/services/guidance_retrieval.py`
  (`GuidanceService`, lazily constructed, never touches Qdrant/the embedder at import time),
  `backend/scripts/index_guidance.py`, and `playbooks/guidance-v1.json` (27 authored,
  illustrative guidance items, one per playbook rule). `rule_engine.py` was not modified —
  retrieval is wired entirely as post-processing enrichment in `job_runner.py`, after
  `evaluate_clauses` has already produced final findings; a new `_attach_guidance` helper
  only ever sets `Finding.guidance_json`. Added the `qdrant` service to `docker-compose.yml`
  behind a new opt-in `retrieval` Compose profile (the `ollama` service now belongs to both
  the `local-model` and `retrieval` profiles, since P4 reuses it for embeddings); no host
  port is published for Qdrant, tighter than Ollama's setup, per `SECURITY_AND_DATA.md`. 101
  backend pytest cases pass (17 new, including a before/after risk-field snapshot test
  proving retrieval cannot alter `rule_id`/`risk_label`/etc. by construction) and 2 frontend
  Vitest cases pass (extended to assert the guidance panel renders and the raw
  `degraded_full_rules` string never appears in the UI). Full live docker-compose validation:
  reset the SQLite volume, confirmed default mode (no profiles) reproduces the exact
  unchanged 8-rule golden fixture with `retrieval_mode: degraded_full_rules`, then brought up
  the `retrieval` profile (Qdrant + Ollama), pulled the embedding model, ran
  `scripts/index_guidance.py`, and confirmed the same 8 findings with real Qdrant-backed
  guidance attached (`retrieval_mode: qdrant`, real cosine-similarity scores) — a direct
  Python diff of both API responses confirmed `review_summary` and all findings/missing
  clauses identical except `finding_id` and `guidance`. Other local Docker projects
  (`ai-boardroom-*`, `omniflow-*`) unaffected throughout. Full detail in
  `IMPLEMENTATION_PHASE_PLAN.md` P4 Completion Notes.
- P4 follow-up fix (Codex finding, non-blocking): `GET /api/v1/health/ready` was still
  reporting the pre-P4 hardcoded `vector_store: "not_configured"` even with Qdrant running.
  Added `check_qdrant_reachable()` to `guidance_retrieval.py` (short 1s timeout, independent
  of the retrieval-path timeout, so the health endpoint never hangs when Qdrant is simply
  absent) and wired it into `routes_health.py`. Verified live in both states
  (`"qdrant"`/`"not_configured"`, ~40ms each); overall `status` unaffected either way. 4 new
  tests; 105 backend tests pass total. P4 remains `complete`; P5 was not started.
- P5 implemented per the approved plan and its 3 corrections: (1) no real cloud adapter
  written — Anthropic/OpenAI/Gemini remain catalog-only, shown as `implemented: false` via
  the new `GET /config/providers`, since D-05 is still `Open`; (2) `PUT /config` now rejects
  (not silently accepts) any `provider_type` outside a new `_SAVEABLE_PROVIDERS = {"ollama"}`
  set, distinct from the display-only `_ALLOWED_PROVIDERS` catalog; (3) `base_url` is
  rejected outright — not silently ignored — both when the effective provider isn't `ollama`
  and when the URL doesn't parse as `http`/`https` with a hostname. Rewrote `AdminModel.tsx`
  from a read-only display into a real form (provider select with disabled "Not enabled"
  options, model name, base URL shown only for Ollama, write-only password-type credential
  field, Save, Test connection with a visible latency/failure result). Added a test-isolation
  fixture (`_reset_config_override` in `conftest.py`) since P5 added the first tests that
  mutate the module-level `_runtime_override` state. 9 new backend tests (114 total, including
  a monkeypatched-Settings test to exercise the base_url-rejected-for-non-ollama branch, which
  is otherwise unreachable purely through the API since `ollama` is the only saveable
  provider) and 6 new frontend tests (8 total) pass. Live-verified in the real browser against
  the running Docker stack: genuine `Connected to ollama (qwen3:4b) in 14ms` test-connection
  result, a submitted invalid base URL rejected inline with the real server error, then a
  valid save succeeding with no console errors — plus the same rejections reconfirmed via
  direct `curl`. Default (no-Ollama) golden-fixture smoke test still reproduces the exact
  unchanged `Critical`/`rule-engine` result. No DB/schema changes, no new ports, no new
  Docker services. Other local Docker projects (`ai-boardroom-*`, `omniflow-*`) unaffected
  throughout. Full detail in `IMPLEMENTATION_PHASE_PLAN.md` P5 Completion Notes.
- P6 implemented per the approved plan and its 5 corrections: (1) SSRF hardening is
  blocklist-first, not "private IPs are safe" — `backend/app/services/ssrf_guard.py` always
  blocks link-local/metadata/reserved/multicast, allows private RFC1918 ranges only in local
  mode (rejected in demo mode), always allows `localhost`/`127.0.0.1`/`ollama`; (2) the new
  `MaxBodySizeMiddleware` is explicitly documented and tested as early rejection only —
  `upload.py`'s post-read size check is unchanged and still authoritative; (3) Qdrant API-key
  auth is optional (unset = unauthenticated, Qdrant's own default) and wired consistently
  through `GuidanceService`, `check_qdrant_reachable`, and `scripts/index_guidance.py` — live
  testing caught a real bug before shipping (an empty-string `QDRANT__SERVICE__API_KEY`
  makes Qdrant start enforcing auth instead of staying unauthenticated), fixed by a
  `Settings` field-validator on the backend side and by deliberately not setting that env var
  on the qdrant Compose service by default; (4) retention is lazy delete-on-read
  (`REVIEW_EXPIRED`, previously dead code) with 5 tests and explicit "PoC retention, not
  production archival" framing in the new evidence doc; (5) added `docs/SECURITY_EVIDENCE.md`
  — factual command/result/date/limitation entries for all 9 areas, including an explicit
  "What P6 does NOT cover" section. Also fixed a real log-redaction gap:
  `job_runner.py`'s blanket exception handler could have echoed quoted document evidence text
  into logs via a `ModelOutputInvalidError` message; now logs exception type + review_id
  only. Added CORS-rejection test evidence (unchanged behavior since P0). Ran a **new**
  egress-blocked verification distinct from P3's (which covered the Ollama+model path) —
  proved the default deterministic path needs zero outbound network access at all, via the
  same `internal: true` Compose network-override technique, with the result diffed
  byte-for-byte identical against a normal-networking baseline. 28 new backend tests (142
  total); frontend untouched (8 tests, unchanged). No schema changes, no new host ports.
  Other local Docker projects (`ai-boardroom-*`, `omniflow-*`) confirmed unaffected
  throughout. Full detail in `IMPLEMENTATION_PHASE_PLAN.md` P6 Completion Notes and
  `docs/SECURITY_EVIDENCE.md`.
- P7 implemented per the approved plan and its 5 corrections: (1) `render.yaml` uses Render's
  free Web Service plan by default, with SQLite on ephemeral container storage explicitly
  documented (no persistent disk on that tier; a paid-plan/disk upgrade path is documented
  but not adopted); (2) D-07 accepted as Render, Docker Web Service; (3) D-05 stays
  deliberately open — the hosted demo is deterministic-only, no provider/Ollama/Qdrant env
  vars are set anywhere in the hosted config; (4) `/admin/model` is hidden from the frontend
  nav in demo mode **and** `PUT /config` is separately, unconditionally backend-locked in
  demo mode (`routes_config.py`), not just UI-hidden; (5) a persistent, non-dismissible
  `DemoModeBanner` states both the synthetic-data warning and the case-study narrative
  disclaimer ("this hosted URL is a synthetic demo convenience... not the target production
  architecture... fully on-premises"), echoed in `README.md`/`DEMO_RUNBOOK.md`/new ADR-012.
  Added `DemoBasicAuthMiddleware` (`backend/app/core/middleware.py`, outermost middleware,
  fails closed if demo mode is on without configured credentials, `/health/live` exempt) and
  `backend/Dockerfile.hosted` (multi-stage: builds the frontend, serves it same-origin from
  the backend via a new SPA-fallback route in `app/main.py`) — entirely additive, the default
  `backend/Dockerfile`/`docker-compose.yml`/local ports are untouched. 7 new backend tests
  (149 total) and 2 new frontend tests (10 total) pass. Verified by building
  `backend/Dockerfile.hosted` locally and exercising it with `docker run`/`curl`: liveness
  open without credentials, config gated by Basic Auth, config writes rejected even
  authenticated, static frontend and a client-side route both served correctly; also
  reconfirmed the default local docker-compose stack and ports are unaffected. **The actual
  live Render deployment (creating the real service, setting the two demo-access secrets in
  the Render dashboard, obtaining a public URL) was explicitly deferred to a later
  polish/optimization phase per user decision — not treated as unfinished P7 work.** Full
  detail in `IMPLEMENTATION_PHASE_PLAN.md` P7 Completion Notes and
  `docs/SECURITY_EVIDENCE.md` section 10.
- Local Compose reliability fix (infra-only, no phase/schema/API change): after a host
  reboot, `docker compose ps` came back empty for this stack and required a manual
  `docker compose up -d --build`, because `backend`/`frontend` had no restart policy.
  Added a top-level `name: legal-contract-review-ai` to `docker-compose.yml` (already the
  effective project name via the folder, now explicit and independent of any future
  directory rename) and `restart: unless-stopped` to `backend`/`frontend` only. `ollama` and
  `qdrant` deliberately keep no restart policy — they stay opt-in-only via their existing
  Compose profiles, so enabling either once doesn't cause a multi-GB model container to
  silently reappear on every reboot. Ports, other Docker projects (`ai-boardroom-*`,
  `omniflow-*`), and all other config are unaffected — see validation below.

## Open Decisions
See `OPEN_DECISIONS.md`. D-07 is accepted (Render, Docker Web Service packaging; the live
deploy itself is deferred to a later polish phase). D-05 remains explicitly open — the
hosted demo is deterministic-only by design, so no real hosted-provider adapter was needed or
built.

## Blockers
No open blocker for P0-P7. The live public Render URL is not a blocker — it is deferred to a
later polish/optimization phase per explicit user decision. Any future real hosted deployment
would still need to revisit the security controls explicitly deferred by P6/P7 (rate
limiting, full SSRF/egress allowlisting, SBOM/vulnerability scanning — see
`docs/SECURITY_EVIDENCE.md`'s "What P6 does NOT cover").

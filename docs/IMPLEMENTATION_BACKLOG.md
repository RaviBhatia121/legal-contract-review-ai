# Part 2 Implementation Backlog

All items are `pending` until implementation begins.

## P0: Foundation and Fixed Result Demo — complete
- [x] Scaffold the documented monorepo with React/Vite frontend and FastAPI backend.
- [x] Add Docker Compose and environment templates.
- [x] Implement health and safe configuration endpoints.
- [x] Implement validated PDF/DOCX upload and review job creation.
- [x] Implement the approved bounded job runner and restart recovery behavior.
- [x] Add SQLite repository boundary for review records.
- [x] Return a schema-valid fixed review result.
- [x] Render review status and structured findings.
- [x] Add P0 golden-path API and UI tests.

## P1: Real Document Parsing — complete
- [x] Generate the synthetic DOCX/PDF fixture and exact expected JSON.
- [x] Parse synthetic PDF and DOCX files locally (`pypdf`/`python-docx`; Docling rejected after offline spike, see `IMPLEMENTATION_PHASE_PLAN.md` P1 notes).
- [x] Implement file validation for unsupported, encrypted, oversized, empty, and non-reviewable files (`DOCUMENT_NOT_APPLICABLE` uses a provisional heuristic; real applicability is P2/P3).
- [x] Implement temporary upload cleanup after success and failure.
- [x] Add parsing and typed-error tests.

## P2: Deterministic Playbook Engine — complete
- [x] Encode the versioned playbook with stable rule identifiers (`playbooks/defense-services-v1.json`).
- [x] Implement applicability checks and typed empty/out-of-scope document failures. (Unchanged from P1's provisional heuristic — not upgraded in P2, deferred to P3.)
- [x] Implement normalized attribute structures for rule evaluation (`backend/app/services/attribute_extraction.py`, fixture-oriented).
- [x] Implement deterministic deviation rules and missing-clause checks (`backend/app/services/rule_engine.py`).
- [x] Implement overall-risk aggregation (max-severity, no averaging).
- [x] Persist immutable review results in SQLite (unchanged repository/model boundary from P0/P1, now populated with real computed clauses/findings).
- [x] Add golden-fixture rule assertion tests (exact 8 rule IDs/counts, PDF and DOCX).

## P3: Model-Assisted Clause Intelligence — complete
- [x] Implement Haystack pipeline components. (`backend/app/services/haystack_pipeline.py`, `AsyncPipeline`, built lazily)
- [x] Implement provider-neutral model adapter. (`backend/app/model_adapter/`; only `OllamaAdapter` implemented, cloud remains P5/D-05)
- [x] Implement local Qwen/Ollama provider. (`OllamaAdapter` against `/api/generate`; Docker Ollama + `qwen3:4b` is the PoC validation target; wiring verified via mocked HTTP server — no live Ollama in this environment)
- [x] Implement clause segmentation and classification contract. (`block_splitter.py`, `clause_intelligence.py`, `ClauseInput`)
- [x] Validate model JSON before rule evaluation. (`schemas/model_io.py`, one-repair-then-fail via `_generate_validated`)
- [x] Add prompt-injection and invalid-model-output tests. (`SYSTEM_INSTRUCTION` matches `PROMPT_SPEC.md`; `test_ollama_adapter.py::test_repair_fails_twice_raises_model_output_invalid`)
- [x] Run a live golden-fixture verification (3 runs, one egress-blocked) against Docker Ollama + `qwen3:4b`. (4/4 runs identical on rule IDs, severities, missing clauses, overall risk, confidences; required an adapter fix from `/api/generate` to `/api/chat` with `think: false` — see `IMPLEMENTATION_PHASE_PLAN.md` P3 Live Verification Notes.)

## P4: Retrieval and Guidance — complete
- [x] Integrate Qdrant supplemental-guidance retrieval with local embeddings without filtering applicable rules. (`backend/app/services/guidance_retrieval.py`; real Qdrant `query_points` per rule, never a JSON lookup)
- [x] Index local guidance and playbook examples. (`playbooks/guidance-v1.json`, 27 items; `backend/scripts/index_guidance.py`)
- [ ] Configure Qdrant authentication and private binding. (No host port published by default, satisfying "never expose its port publicly" for local dev; formal authentication is P6's "Qdrant private binding/auth" exit criterion, not duplicated here.)
- [x] Implement degraded retrieval mode when Qdrant is unavailable. (Verified live: default `docker compose up` — no Qdrant — reproduces the exact unchanged golden fixture with `retrieval_mode: degraded_full_rules`.)
- [x] Add tests proving Qdrant cannot change applicable rule IDs or severities. (`test_guidance_attachment.py`'s before/after risk-field snapshot, plus a live docker-compose diff of retrieval-on vs retrieval-off API responses — see `IMPLEMENTATION_PHASE_PLAN.md` P4 Completion Notes.)

## P5: Admin and Provider Configuration — complete
- [x] Add Demo mode banner. (`frontend/src/components/DemoModeBadge.tsx`, pre-existing since P0, wired into `App.tsx`'s header; shows "Demo mode — synthetic data only" when `deployment_mode === "demo"`.) **Not done, out of P5's approved scope:** a synthetic-data acknowledgement checkbox on the upload screen (`UI_SPEC.md` Review Screen) — the approved P5 plan scoped this phase to admin/provider configuration only, not the upload flow; deferred, not silently completed.
- [x] Implement admin provider configuration UI. (`AdminModel.tsx` rewritten as an editable form: provider select, model name, base URL, write-only credential, Save, Test connection — see `IMPLEMENTATION_PHASE_PLAN.md` P5 notes.)
- [x] Implement server-side secret handling and redacted configuration APIs. (Unchanged, already correct since P0/P3: credential is write-only, never returned, held only as a boolean `has_credential` flag — verified by test that the submitted value never appears in any response.)
- [ ] Implement selected hosted model adapter after D-05 is accepted or replaced. (Explicitly **not done** — D-05 remains Open; P5 demonstrates provider portability via UI/catalog/interface only, per the approved corrections.)
- [x] Ensure only implemented, allowlisted providers can be selected. (`PUT /config` rejects any `provider_type` not in `_SAVEABLE_PROVIDERS = {"ollama"}` — verified live and by test; catalog still shows all 4 for display via `GET /config/providers`.)

## P6: Security and Evidence Hardening — complete
- [x] Add upload limits, timeouts, CORS allowlist, and endpoint validation. (Upload size limit since P1; `MaxBodySizeMiddleware` adds an early `Content-Length`-based rejection layer in P6; CORS allowlist unchanged since P0, now with explicit test evidence.)
- [x] Add SSRF protections and restricted endpoint validation. (`backend/app/services/ssrf_guard.py` — blocklist-first: always blocks link-local/metadata/reserved/multicast, private ranges gated to local mode only, fixed hostnames always allowed. Full DNS/IP-range allowlisting beyond this remains a disclosed limitation, not enterprise-grade egress policy.)
- [x] Add logging redaction for secrets and document bodies. (`job_runner.py`'s blanket exception handler now logs exception type + review_id only; verified with a `caplog` test forcing a failure carrying fake secret/evidence sentinels.)
- [x] Add retention cleanup for records. (Lazy delete-on-read in `GET /reviews/{id}`, `REVIEW_EXPIRED` — explicitly documented as PoC retention, not production archival, in `docs/SECURITY_EVIDENCE.md`. "Vectors" retained from the original wording don't apply — see P4's correction that Qdrant stores no per-review data.)
- [x] Verify no unintended telemetry or external document-processing calls. (Already closed in P3 — `HAYSTACK_TELEMETRY_ENABLED=False` set before any `haystack` import; re-confirmed as part of P6's egress-blocked verification that the default path makes zero outbound calls.)
- [x] Run functional, security, and adversarial tests. (28 new backend tests: SSRF, upload-size-guard, log-redaction, retention, Qdrant-auth, CORS. Prompt-injection/adversarial-fixture tests already existed since P2.)
- [x] Record three pinned local-model runs, including a successful egress-blocked run and confidence variance. (Already satisfied by P3's live verification — cross-referenced in `docs/SECURITY_EVIDENCE.md`, not redone. P6 adds a *new*, separate egress-blocked verification for the default deterministic path specifically.)
- [ ] Run Unicode/Indonesian preservation test and optional Indonesian smoke review. (Not in this P6 pass's approved focus areas — remains backlog, deferred rather than silently expanding scope.)

## P7: Hosted Demo and Polish — complete
- [x] Resolve D-07 hosting platform before deployment packaging. (Accepted: Render, Docker
  Web Service — `render.yaml`, `backend/Dockerfile.hosted`. Persistence marked ephemeral on
  the default free plan; paid-disk upgrade path documented but not adopted.)
- [x] Add access restriction and TLS at ingress. (Access: app-level `DemoBasicAuthMiddleware`,
  fails closed if unconfigured, D-06. TLS: provided automatically by Render's ingress —
  hosted path only, local dev stays plain HTTP by design.)
- [x] Backend-lock `PUT /config` in hosted demo mode, not just hide the admin nav link.
  (`routes_config.py` rejects unconditionally when `deployment_mode: demo`; verified via
  automated test and a direct authenticated `curl PUT` against the built hosted image.)
- [x] Same-origin frontend/backend serving for the hosted image. (`backend/Dockerfile.hosted`
  multi-stage build + `app/main.py` SPA-fallback route; no cross-origin case for the hosted
  deployment's own UI.)
- [x] Demo banner and case-study narrative disclaimer. (`DemoModeBanner` — persistent,
  non-dismissible, states synthetic-data-only and "not the target production architecture...
  fully on-premises," echoed in `README.md`/`DEMO_RUNBOOK.md`/ADR-012.)
- [x] Build and verify the hosted image locally. (`docker build -f backend/Dockerfile.hosted`,
  ran with `docker run`, verified auth/config-lock/static-serving/SPA-fallback via `curl` —
  see `docs/SECURITY_EVIDENCE.md` §10.)
- [x] Confirm the default local docker-compose stack, ports, and other Docker projects are
  unaffected. (Live smoke test of `backend` service unchanged; `docker compose config` shows
  ports still 8420/5420.)
### Deferred to a later polish/optimization phase (not P7 exit criteria)
Per explicit review decision, going live on a real public URL is out of P7's 2-day
implementation scope. All packaging needed for it is already committed and verified; only
the deploy action itself and its downstream evidence are deferred.
- [ ] Deploy the hosted synthetic-data Demo mode URL. (Requires a live Render account; run
  the committed `render.yaml` against `backend/Dockerfile.hosted` when this later phase is
  authorized, per `docs/DEMO_RUNBOOK.md`.)
- [ ] Capture screenshots and example API output from the **live** hosted URL. (Local
  hosted-image evidence already captured as a substitute for this pass, `SECURITY_EVIDENCE.md`
  §10; live-URL screenshots follow the deploy step above.)
- [ ] Complete the demo runbook's remaining `TBD` fields (hosted URL, generated fixture
  artifact) — follows the deploy step above; everything else in the runbook is filled in.
- [ ] Generate dependency/license report and SBOM. (Still not done — disclosed since P6,
  remains out of scope for both P7 and this later phase's minimum bar.)
- [ ] Complete architecture walkthrough. (Docs are reconciled per `CHANGE_CONTROL.md`; a
  live spoken/recorded walkthrough is a presentation-time activity, not a repo artifact.)

## Sequence Rule
Follow `IMPLEMENTATION_PHASE_PLAN.md`. Complete P0 before real parsing, complete P1 before deterministic rule evaluation, and complete P2 before model-provider complexity. Do not start hosted-provider work until D-05 is accepted or replaced. Do not deploy until D-07 is accepted or replaced and the applicable security checks in `TEST_AND_ACCEPTANCE_PLAN.md` pass.

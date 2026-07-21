# Part 2 Implementation Phase Plan

## Purpose
Define incremental delivery phases for Part 2 implementation. Each phase must add working capability and leave the documentation pack reconciled before the next phase begins.

## Status Key
- `pending`: not started
- `in_progress`: active implementation
- `blocked`: cannot proceed without a decision, dependency, or correction
- `complete`: implemented, verified, and documentation updated

## Phase Rule
At the end of every phase:
1. Read `MASTER_INDEX.md`.
2. Review all specifications affected by the phase.
3. Update `PLAN.md`, `AGENT_HANDOFF.md`, `IMPLEMENTATION_BACKLOG.md`, and any changed functional, API, schema, architecture, security, fixture, or test docs.
4. Update `TRACEABILITY_MATRIX.md` when requirement coverage changes.
5. Run the applicable tests or checks for that phase and record gaps honestly.
6. Do not mark the phase `complete` until code, verification evidence, and documentation are aligned.

## Phases

| Phase | Status | Technical Delivery | Feature Delivery | Exit Criteria |
|---|---|---|---|---|
| P0 Foundation and Fixed Result Demo | complete | Monorepo scaffold, FastAPI backend, React/Vite frontend, SQLite boundary, health/config endpoints, upload/job skeleton, schema-valid fixed review result | User can upload the synthetic fixture and see structured Legal risk findings end to end | App runs locally; upload creates a job; result matches `OUTPUT_SCHEMA.md`; UI renders findings; docs updated |
| P1 Real Document Parsing | complete | pypdf/python-docx PDF/DOCX parsing (Docling rejected after spike; see notes), file validation, typed errors, temporary upload cleanup | System reads uploaded contract text and handles invalid, empty, encrypted, oversized, and non-reviewable files safely | PDF/DOCX text extraction works; failure cases return documented errors; tests cover upload/parsing paths; docs updated |
| P2 Deterministic Playbook Engine | complete | Encoded defense playbook (`playbooks/defense-services-v1.json`), fixture-oriented deterministic segmentation/attribute extraction, deterministic rule evaluator, missing-clause checks, risk aggregation | Findings are produced from extracted/normalized contract evidence and mapped to rule IDs/severities | Golden fixture returns exact expected rule IDs/counts; summary matches findings; rule tests pass; docs updated |
| P3 Model-Assisted Clause Intelligence | complete | Haystack pipeline, provider-neutral model adapter, Docker Ollama/Qwen local path (opt-in), structured JSON validation, prompt-injection resistance | AI assists clause classification and attribute extraction while application rules still own decisions | Docker Ollama `qwen3:4b` path completes fixture (**verified live**, 3/3 runs plus 1 egress-blocked run, identical rule IDs/severities/missing-clauses/overall-risk/confidences); invalid model JSON fails safely (verified, mocked); fixed fallback remains separate from acceptance evidence (verified); docs updated |
| P4 Retrieval and Guidance | complete | Qdrant integration (real queries, not a JSON lookup), local `qllama/multilingual-e5-small` embeddings via Docker Ollama, authored guidance corpus (27 items), degraded retrieval mode | Findings can show supplemental guidance without retrieval controlling rule applicability | Qdrant ranks guidance only (**verified live**: retrieval-on vs retrieval-off produce byte-identical rule IDs/severities/missing-clauses/overall-risk); complete rule set is always evaluated; degraded mode preserves fixture outcome (verified, Qdrant unreachable); docs updated |
| P5 Admin and Provider Configuration | complete | Editable admin config API/UI, redacted secrets, provider catalog (`GET /config/providers`), Ollama endpoint settings with reject-not-ignore validation; no hosted-provider adapter (D-05 remains open) | Admin can demonstrate provider portability and Demo mode without exposing credentials | Config never returns secrets (verified); only `ollama` selectable/saveable, others shown "Not enabled" and rejected server-side if submitted (verified live); `base_url` rejected for non-ollama or invalid format (verified live); docs updated |
| P6 Security and Evidence Hardening | complete | SSRF hardening (mode-gated blocklist), defense-in-depth upload size guard, log redaction, PoC retention enforcement, optional Qdrant API-key auth, CORS/egress evidence, `docs/SECURITY_EVIDENCE.md` | Prototype has credible defense-sector security evidence and local-model verification | Security tests pass (verified, 26 new backend tests); local egress-blocked default-mode fixture run captured (**verified live**, byte-identical to normal-networking baseline); three-run local-model variance already recorded in P3 (cross-referenced, not redone); docs updated |
| P7 Hosted Demo and Polish | complete | Deployment packaging (`backend/Dockerfile.hosted`, `render.yaml`), D-07 accepted as Render, hosted-demo Basic Auth access gate, backend-locked config in demo mode, same-origin frontend/backend serving, demo banner + case-study narrative disclaimer | Deployable hosted-demo image presents a polished synthetic demo workflow and case-study narrative | Hosted image built and verified locally against every check a live deploy would need (see `SECURITY_EVIDENCE.md` §10); D-07 accepted (Render, packaging), D-05 deliberately stays open (deterministic-only hosted demo); docs updated. **Explicitly deferred to a later polish/optimization phase, by decision, not a P7 exit-criteria gap:** actually running the committed `render.yaml`/`backend/Dockerfile.hosted` against a live Render account to obtain a public URL — `docs/DEMO_RUNBOOK.md`'s hosted URL and generated-fixture-artifact fields stay `TBD` until that later phase. |
| P8 UI/UX and Demo Polish | complete | Dashboard/history API and UI, product branding, upload-screen playbook/local-processing explanation, findings readability, admin visual polish, read-only playbook viewer, final validation | Prototype feels like a credible intranet legal AI product while preserving the structured non-chat workflow | `GET /reviews` summary list works without leaking evidence/full findings and respects retention (**done, P8.1**); dashboard metrics are real (**done, P8.3**); branding/default scaffold feel removed (**done, P8.2**); upload screen explains the playbook/pipeline/output honestly without on-premises claims (**done, P8.4**); findings screen is scannable, discloses decision-support/rule-engine-sourced risk/non-scoring guidance, and preserves every field (**done, P8.5**); admin screen demonstrates provider portability without enabling cloud adapters or exposing credentials (**done, P8.6**); read-only Admin Playbook viewer exposes active playbook/rules without CRUD (**done, P8.8**); no rule/model/retrieval behavior changes; backend tests 163/163, frontend tests 33/33, frontend build, Docker health, live upload smoke test, and docs reconciliation passed |
| P9 Case-Study Alignment | complete | `/architecture` stack/data-flow page, approved-template drafting support keyed by rule ID, explicit Qdrant guidance status cards | Reviewer can see the required local tech stack/model/vector DB/backend/frontend walkthrough, Legal drafting support, and retrieval status without ambiguity | Backend 164/164 passed; frontend 38/38 passed; frontend build clean; Docker rebuilt; live upload completed with model mode, no fallback, Critical risk, and approved-template draft support on every finding/missing-clause item |

## Dependency Notes
- P0-P9 are complete and verified. Historical P3 evidence includes a live Docker Ollama +
  `qwen3:4b` golden-fixture run; the current browser-demo runtime uses the shared on-prem
  Ollama VM (`http://<ollama-vm-ip>:11434`, `qwen3.6:35b`) so the laptop does not run a
  heavy local model. Verification also includes a live Qdrant + local-embedding retrieval run (P4), a live admin config
  save/reject/test-connection verification (P5), live security-control verification
  including an egress-blocked default-mode run (P6, see `SECURITY_EVIDENCE.md`), and a
  hosted-demo packaging verification against the built hosted image run locally (P7, see
  `SECURITY_EVIDENCE.md` §10), and P8 UI/UX final validation (backend 163/163, frontend
  33/33, frontend build, Docker health, and live upload-to-findings smoke test). P9 closes the
  remaining case-study alignment gap by exposing the stack/data-flow page, approved-template
  drafting support, and explicit Qdrant guidance visibility.
- P5 implemented provider-portability UI/catalog/interface only — no real hosted-provider
  adapter. Real Anthropic/OpenAI/Gemini integration remains blocked on D-05 being accepted.
- AI fallback transparency is implemented after P8: model-mode execution records
  `mode_requested`, `mode_used`, `fallback_used`, and `fallback_reason`, and the UI visibly
  labels fallback reviews instead of implying model-assisted output. See
  `AI_MODEL_FALLBACK_APPENDIX.md`.
- P6 deliberately does not implement authentication, TLS, rate limiting, or full
  enterprise-grade SSRF/egress allowlisting — see `SECURITY_EVIDENCE.md`'s "What P6 does NOT
  cover" section.
- P7 is complete: it implements the hosted-demo packaging and every control planned for it
  (D-07 accepted as Render; demo access auth; backend-locked config; same-origin serving),
  all verified against the built hosted Docker image run locally. D-05 stays deliberately
  open — the hosted demo is deterministic-only, so no hosted model provider was needed.
  Actually deploying the committed `render.yaml` / `backend/Dockerfile.hosted` to a live
  Render account to get a real public URL is **explicitly deferred to a later
  polish/optimization phase, by decision** — not treated as unfinished P7 scope.
  `docs/DEMO_RUNBOOK.md` documents exactly what to fill in once that later deploy happens.
- P8 UI/UX and demo polish is complete. It is governed by `P8_UI_UX_POLISH_PLAN.md` and did
  not change rule logic, model behavior, retrieval behavior, hosting/live URL status, or
  PDF/export packaging.
- Do not skip P0; each later phase assumes the previous phase is runnable.

## P0 Completion Notes
- Backend: FastAPI app (`backend/app`) with SQLite via SQLAlchemy async + aiosqlite, a
  `ReviewRepository` boundary, `POST/GET/DELETE /api/v1/reviews`, `GET/PUT /api/v1/config`,
  `POST /api/v1/config/test`, and `GET /api/v1/health/live|ready`, matching `API_CONTRACT.md`.
- Job execution: bounded in-process async job runner (`backend/app/core/job_runner.py`)
  progresses a review through the `current_stage` sequence from `OUTPUT_SCHEMA.md`, then
  writes a **fixed result**, not real parsing or rule evaluation. Restart recovery marks
  interrupted active jobs `failed` with `JOB_INTERRUPTED`.
- Fixed result: the full 8-finding `Sentinel Systems Support Services Agreement` result
  from `DEMO_FIXTURE_SPEC.md` is hardcoded in `backend/app/fixtures/fixed_result.py` and
  returned for every review, regardless of uploaded file content. `document.name`/`sha256`
  reflect the real uploaded file; other fields (page_count, language, clause text) are fixed
  placeholders until P1 parsing exists.
- Frontend: React/TS/Vite app (`frontend/src`) with `/review/new`, `/reviews/:reviewId`
  (status + findings), and `/admin/model` (read-only config display), matching `UI_SPEC.md`.
- Tests: 7 backend pytest cases (health, config, upload validation, golden-path review
  flow, 404 handling) and 2 frontend Vitest/Testing Library cases (upload validation,
  upload-to-findings render) all pass. `npm run build` and `python -m pytest -q` both green.
- Docker Compose: `docker-compose.yml` builds and runs both services; verified locally
  with `docker compose up --build` including cross-container API proxying from the
  frontend container to the backend container.
- Known P0 limitations carried into P1: no real file parsing, page-count/encryption
  validation, or rule evaluation; `PUT /config` and `POST /config/test` are stubs with no
  real provider call; admin screen is read-only (no save/test UI wiring yet).

## P1 Completion Notes
- **Docling spike rejected the planned parser.** `docling==2.113.0`'s default PDF pipeline
  unconditionally attempts to download layout/OCR model weights from HuggingFace Hub on
  first use, even with `do_ocr=False` and for a purely text-native PDF — confirmed by
  running with a poisoned proxy and observing a `ConnectError`/`LocalEntryNotFoundError`
  from the layout-model download path. This has no pre-provisioning story until P6, so P1
  uses `pypdf` (PDF) and `python-docx` (DOCX) instead — both verified offline, fast import
  (<1s), zero network calls. Docling remains the documented future parser target once
  artifact pre-provisioning exists; see `TECH_STACK_AND_LICENSES.md`.
- Parsing service: `backend/app/services/parsing.py` wraps `pypdf`/`python-docx`, raising
  typed exceptions (`EncryptedDocumentError`, `DocumentTooLongError`,
  `DocumentParseFailedError`) mapped to `ENCRYPTED_DOCUMENT`, `DOCUMENT_TOO_LONG`,
  `DOCUMENT_PARSE_FAILED`. DOCX has no reliable native page count; page count for DOCX is a
  documented word-count-based estimate used only for the 100-page limit check. Language
  detection is not implemented in P1 (no detection library was approved this phase);
  `document_language` defaults to `"en"` for any non-empty text, `"unknown"` for empty text.
- Applicability: `backend/app/services/applicability.py` implements `NO_REVIEWABLE_TEXT`
  (text-length floor) fully, and a **provisional, explicitly non-final** word-count
  heuristic for `DOCUMENT_NOT_APPLICABLE`. Real semantic applicability requires clause
  classification and is P2/P3 scope; this heuristic only exists to give the
  `non-contract.pdf` fixture a typed rejection path in P1 and must not be read as real
  applicability judgment.
- Temp-file handoff: upload bytes are written server-side to `Review.upload_temp_path`
  (restrictive permissions, server-generated filename) at review creation, before the job
  is scheduled. The job runner reads that path, deletes the file in a `finally` block
  immediately after the parse attempt (success or failure), and both `mark_completed` and
  `mark_failed` null the DB column. `recover_interrupted_jobs` defensively deletes any
  temp file left behind by a review interrupted mid-job before marking it failed.
- Data model: added `Review.upload_temp_path`, `parsed_text`, `parser_name`,
  `parser_version`, `parse_error_code` (all nullable, internal-only — never serialized to
  the API). See `DATA_MODEL.md`.
- P1 boundary honored as scoped: clause/finding content still comes from the P0 fixed
  fixture (`backend/app/fixtures/fixed_result.py`) after parsing succeeds; only
  `document.page_count`, `document.language`, and `provenance.parser_name/parser_version`
  now reflect the real parsed document. P2 replaces the fixed clauses/findings with real
  rule evaluation over `Review.parsed_text`.
- Fixtures: `scripts/generate_fixtures.py` (requires `pip install -e ".[fixtures]"` for the
  `reportlab` build-time-only dependency, not part of the runtime image) generates and the
  repo commits `fixtures/sentinel-support-agreement.{docx,pdf}`,
  `fixtures/sentinel-support-agreement.expected.json`, `fixtures/invalid.txt`,
  `fixtures/empty.pdf`, `fixtures/non-contract.pdf`. The generated PDF is 8 pages, 770
  words, and includes the required adversarial appendix sentence verbatim in both formats.
  `expected.json` is the target result for P2's real rule engine, not current P1 output; it
  records page numbers measured from the actual generated PDF. The oversized-file and
  encrypted-file test cases are generated inline by tests, not committed, per
  `DEMO_FIXTURE_SPEC.md`.
- Tests: 23 backend pytest cases pass (16 new: parsing unit tests, applicability unit
  tests, golden-path DOCX case, `NO_REVIEWABLE_TEXT`/`DOCUMENT_NOT_APPLICABLE`/
  `ENCRYPTED_DOCUMENT`/`DOCUMENT_PARSE_FAILED` end-to-end cases, temp-cleanup assertion).
  Frontend suite unchanged and still green (no frontend code changes in P1). Full
  `docker compose up --build` smoke test performed with the real fixture PDF, an empty PDF,
  and a non-contract PDF, confirming real `page_count`/`language`/`parser_name` in the API
  response and an empty upload-temp directory inside the container after processing.
- Known P1 limitations carried into P2/P3: no real language detection; `DOCUMENT_NOT_APPLICABLE`
  is a narrow provisional heuristic, not real applicability judgment; DOCX page count is an
  estimate; clauses/findings remain the P0 fixed fixture, not derived from `parsed_text`.

## P2 Completion Notes
- **Machine-readable playbook**: `playbooks/defense-services-v1.json` transcribes
  `DEFENSE_PLAYBOOK_TEMPLATE.md`'s full rule table (27 rules) and required-clause mapping
  verbatim. Loaded/validated by `backend/app/playbook/loader.py` (cached, typed
  dataclasses). Backend Docker build context moved from `backend/` to the repo root so the
  image can `COPY playbooks ./playbooks`; a root `.dockerignore` was added; see
  `REPOSITORY_STRATEGY.md`.
- **Segmentation and extraction are explicitly fixture-oriented, not general** (correction
  #4 from the approved plan): `backend/app/services/segmentation.py` recognizes this one
  fixture's "Section N. Title" / "N.M" heading convention;
  `backend/app/services/attribute_extraction.py` matches phrases known to appear in that
  exact document. Both modules' docstrings and several inline comments state this
  boundary explicitly. A differently structured or worded contract will not segment or
  extract correctly — that is expected P2 behavior, not a defect; general, model-assisted
  extraction is P3 scope.
- **Canonical `clause_type` enum adopted**: switched from the P0/P1 fixed-result's ad hoc
  strings (`subcontractors`, `liability`, `termination`, `security`) to
  `DEFENSE_PLAYBOOK_TEMPLATE.md`'s canonical enum (`subcontracting`,
  `liability_indemnity`, `termination_exit`, `security_incident`, etc.), since P2 is the
  first phase where `clause_type` is rule-lookup-load-bearing. See `DATA_MODEL.md`.
- **Rule engine** (`backend/app/services/rule_engine.py`): evaluates all 27
  `RULE_EVALUATION_SPEC.md` predicates in ascending rule-ID order per clause type,
  implements the `AUD-001` dual-purpose behavior (missing_clause when the audit clause is
  absent, deviation when present but insufficient), confidence-banding (`REV-001` below
  0.60, `needs_review` in the 0.60-0.79 band), and max-severity risk aggregation (no
  averaging). Confidence is a deterministic pattern-match-strength heuristic (matched known
  phrase → 0.95, recognized-but-unmatched → 0.45), not a model probability — there is no
  model anywhere in P2.
- **Applicability stays untouched** (correction #3): `DOCUMENT_NOT_APPLICABLE` remains
  P1's provisional word-count heuristic; real, general applicability judgment (requiring
  clause classification) is deferred fully to P3/later, not attempted in P2.
- **`backend/app/fixtures/fixed_result.py` removed** (correction #2: kept until P2 tests
  passed and the file was confirmed fully unreferenced, then deleted in this change set,
  along with the now-empty `app/fixtures/` package).
- **Provenance honesty**: `provenance.model_provider`/`model_name` are `"rule-engine"`/
  `"none"` in P2 (previously `"fixed-fixture"`/`"none"`); `source` is `"rule"` on every P2
  finding, never `"model_assisted_rule"`.
- **UI/demo narrative check** (correction #4): grepped the frontend for overclaiming
  language ("understand", "AI-powered", "intelligent", etc.) — none found; no UI changes
  were needed or made in P2.
- Tests: 68 backend pytest cases pass (45 new: playbook loader, segmentation, attribute
  extraction, 27 rule predicates + aggregation, REV-001 boundary, `AUD-001` dual-purpose,
  adversarial-sentence resistance, golden-fixture PDF+DOCX exact-match assertions). Full
  `docker compose up --build` smoke test (rebuilt with the new build context) confirmed the
  real rule engine runs correctly inside the container: exact 8 golden findings,
  `model_provider: rule-engine`, frontend proxy unaffected. Other locally running Docker
  projects were unaffected throughout.
- Known P2 limitations carried into P3: segmentation/extraction only work on this one
  fixture's known structure and wording; confidence is a pattern-match heuristic, not a
  real classifier; `DOCUMENT_NOT_APPLICABLE` is still the P1 provisional heuristic;
  `Review.playbook_version` is a static default that happens to match the loaded
  playbook's version rather than being dynamically set from it (low-risk, noted for
  future cleanup, not a correctness issue today).

## P3 Implementation Notes — status `complete`
- **Spike (go/no-go, applied the 3 approved corrections):** `haystack-ai==2.31.0` installed
  cleanly (~6s, ~136MB, no torch/transformers, unlike the Docling spike). Custom async
  components (`@component` with both a stub sync `run` and a real `run_async`) verified
  working end to end via `AsyncPipeline.run_async`, confirmed against a mocked Ollama HTTP
  server (JSON-mode request/response/Pydantic-validation round trip). Go decision.
- **Provider-neutral adapter, Ollama-only implemented:** `backend/app/model_adapter/`
  (`base.py` Protocol, `ollama_adapter.py`, `errors.py`). Cloud providers
  (Anthropic/OpenAI/Gemini) are **not implemented** — selecting them returns
  `PROVIDER_UNAVAILABLE` honestly (P5/D-05, not silently introduced).
- **Haystack pipeline, built lazily** (correction #2): `ClauseClassifierComponent` and
  `AttributeExtractorComponent` (`backend/app/services/haystack_pipeline.py`), assembled by
  `ClauseIntelligenceService._build_pipeline` only when a review actually reaches the model
  path — never at module import time, so app startup never depends on Ollama being
  reachable. Confirmed via `python -c "from app.main import app"` succeeding with no Ollama
  running.
- **Runtime default split:** `Settings.clause_intelligence_mode` keeps a safe code-level
  default of `"deterministic"` for tests/non-Compose runs, while local Docker Compose now
  defaults to model-assisted mode against the shared on-prem Ollama VM. If the model path is
  unavailable, review processing falls back to rules-only output with explicit provenance/UI
  disclosure.
- **`rule_engine.py` refactored, not rewritten:** extracted `evaluate_clauses(clause_inputs,
  playbook, source=...)` as the reusable, extraction-source-agnostic core; `evaluate_document`
  (P2 path) and the new P3 model path both funnel into it. All 27 pre-existing predicate
  tests pass unchanged, proving the refactor is behavior-preserving. `ClauseInput` is the
  new shared, source-agnostic contract. `Finding.source` is `"model_assisted_rule"` for
  evidence-based findings from the model path, `"rule"` for the deterministic path and
  always for missing-clause findings (no clause evidence to attribute to a model).
- **General block splitter** (`backend/app/services/block_splitter.py`): paragraph/
  length-based chunking with page attribution, makes no assumption about document
  structure — unlike P2's `segmentation.py`, which is deliberately fixture-tuned.
- **`DOCUMENT_NOT_APPLICABLE` upgraded and relocated:** now a real, source-agnostic check
  (`backend/app/services/applicability.is_applicable`) requiring >= 2 required clause types
  classified at >= 0.60 confidence, run immediately after classification instead of before
  it (`WORKFLOW_SPEC.md` stage-order correction, both docs and `job_runner.py` updated in
  this change set). Runs identically for both extraction paths.
- **`/config/test` upgraded, backend-only** (correction #3, no admin UI editing/save work —
  still P5): real `GET /api/tags` Ollama reachability ping for `provider_type: ollama`;
  honest `PROVIDER_UNAVAILABLE` for any other provider.
- **`docker-compose.yml`:** after the shared-VM follow-up, `backend` and `frontend` remain
  restart-enabled, while laptop-local `ollama` is profile-gated (`--profile local-model`) and
  not started by default. Docker Compose defaults review processing to model-assisted mode
  against the shared on-prem Ollama VM; if that path is unavailable, reviews fall back to
  rules-only with explicit API/UI disclosure.
- **Telemetry disabled:** `haystack-ai` pulls in `posthog` transitively;
  `HAYSTACK_TELEMETRY_ENABLED=False` set in `backend/app/__init__.py` (before any `haystack`
  import) and redundantly in `docker-compose.yml`.
- **Tests:** 82 backend pytest cases pass (14 new: `OllamaAdapter` against a local stdlib
  mock HTTP server covering success/timeout/repair-once/repair-fails-twice/ping,
  `AsyncPipeline` component wiring with a fake adapter, `ClauseIntelligenceService`
  deterministic/model-mode dispatch, `evaluate_clauses` source-labeling, and the new
  `applicability.is_applicable` behavior replacing the old word-count heuristic). Full
  `docker compose up --build` smoke test in default (deterministic) mode confirmed the exact
  8 golden findings and a clean `PROVIDER_UNAVAILABLE` `/config/test` response with no
  Ollama running; other locally running Docker projects unaffected throughout.
## P3 Live Verification Notes — closes the prior `blocked` status

Performed with explicit user approval to use Docker-based Ollama, pull `qwen3:4b`, and keep
everything inside Docker Compose (no host-installed Ollama). Backend/frontend containers
were rebuilt with `CLAUSE_INTELLIGENCE_MODE=model MODEL_NAME=qwen3:4b`; the `ollama` service
was started via `docker compose --profile local-model up -d ollama`, and `qwen3:4b` was
pulled inside the container (`docker compose exec ollama ollama pull qwen3:4b`, 2.5GB,
~10 minutes).

- **Adapter fix required to unblock verification (`ollama_adapter.py`):** the first live
  attempt failed — `/api/generate` (raw completion, no chat template) cannot suppress
  qwen3:4b's reasoning/"thinking" behavior. Reproduced directly against the running
  container: the model's full JSON answer was generated correctly but Ollama routed the
  entire output into the discarded `thinking` field, leaving `response` empty (confirmed via
  a raw `curl` reproduction against `/api/generate` with the real fixture text — `response`
  was `""` after 163s and 1817 generated tokens, all of it sitting in `thinking`). Fixed by
  switching the adapter from `/api/generate` to `/api/chat` with `"think": false` and a
  proper `messages` array — verified this correctly returns the answer in
  `message.content` with `thinking: null`. This is a real adapter-correctness fix required
  for any reasoning-capable local model, not a prompt or scope change; `PROMPT_SPEC.md`'s
  existing "no hidden reasoning" requirement was already correct, `/api/generate` just
  couldn't enforce it for this model family. Updated `backend/tests/test_ollama_adapter.py`'s
  mock envelope to the `/api/chat` response shape. All 82 backend tests still pass.
- **Config change:** `PART2_OLLAMA_TIMEOUT_S` was not previously exposed through
  `docker-compose.yml`; added it (`${OLLAMA_TIMEOUT_S:-60}`, default unchanged) so it can be
  overridden for real CPU inference, which is far slower than the mocked tests (~2-3 minutes
  per model call on this hardware: 14 vCPU, no GPU passthrough). Set to 300s for live
  verification.
- **3-run + 1 egress-blocked run, `fixtures/sentinel-support-agreement.pdf`, real API
  (`POST /api/v1/reviews`), full pipeline (parse -> classify -> extract -> evaluate):**

  | Run | Overall Risk | Findings | Rule IDs | Missing Clauses | Confidences | needs_review |
  |---|---|---|---|---|---|---|
  | 1 | High | 7 | DATA-002, LIAB-002, SUB-002, TERM-001, TERM-002 | AUD-001, SEC-004 | all 0.9 | 0 |
  | 2 | High | 7 | (identical to Run 1) | (identical) | all 0.9 | 0 |
  | 3 | High | 7 | (identical to Run 1) | (identical) | all 0.9 | 0 |
  | Egress-blocked | High | 7 | (identical to Run 1) | (identical) | all 0.9 | 0 |

  All four runs are byte-identical on rule IDs, severities, missing clauses, overall risk,
  and confidence values — full repeatability at `temperature: 0` on this hardware. Every
  run's `provenance.model_provider`/`model_name` were `ollama`/`qwen3:4b`; every
  evidence-based finding had `source: "model_assisted_rule"`; both missing-clause findings
  had `source: "rule"` — exactly as specified.
- **Egress-blocked run method:** recreated the Compose network as `internal: true` (temporary
  override, not committed) with `backend`+`ollama` attached and `frontend` stopped. Confirmed
  egress was genuinely blocked before, during, and after the run (`urllib` from inside the
  backend container raised `OSError: Network is unreachable` against `1.1.1.1`), while
  backend-to-ollama container-to-container traffic on the same internal network kept working
  (`/config/test` still returned `ok: true` with live latency). `internal: true` also drops
  the host port mapping, so the API was driven from `docker compose exec backend` using
  `urllib` (no `curl` in the slim image) rather than via `localhost:8420`. Reverted to normal
  networking afterward and confirmed the default deterministic path still reproduces the
  exact 8-rule golden fixture unchanged.
- **This run's findings vs. P2's deterministic golden fixture — expected, disclosed
  divergence, not a bug:** the model path finds different rule IDs (DATA-002/LIAB-002/
  SUB-002/TERM-001/TERM-002 vs. P2's DATA-001/CONF-002/SUB-001/AUD-001/IP-002/LIAB-001/
  TERM-004/SEC-002) and a different overall risk (High vs. Critical) than P2's
  fixture-tuned deterministic path, because it is a genuinely different clause
  classification (`clauses_reviewed: 6` vs. P2's fuller fixture-tuned segmentation), not a
  different rule engine — `evaluate_clauses` is the identical, unchanged code for both paths.
  `TEST_AND_ACCEPTANCE_PLAN.md`'s Repeatability Tests section explicitly anticipates this:
  "a fixed fixture result cannot satisfy this criterion" and the acceptance bar is 3-run
  self-consistency, not reproducing P2's exact numbers. **Quality caveat, disclosed
  honestly:** `qwen3:4b` did not classify or flag findings for `confidentiality`,
  `ip_ownership`, or `security_incident`-adjacent clause types that are present in the
  fixture text (visible in the classify prompt's own extracted evidence), even though it
  found `security_incident` as a *missing* clause. This is a real, observed model-quality
  limitation of the lightweight PoC model on this task — recorded here and in
  `RISK_REGISTER.md` R-03 rather than hidden. It does not block the exit criterion as
  written, but should inform any decision to use `qwen3:4b` output for real legal review
  guidance rather than workflow demonstration.
- **Cleanup:** the temporary egress-block Compose network override was not committed to the
  repo; only `docker-compose.yml`'s new `PART2_OLLAMA_TIMEOUT_S` line and
  `ollama_adapter.py`'s `/api/chat` fix are permanent changes. Other locally running Docker
  projects (`ai-boardroom-*`, `omniflow-*`) were confirmed unaffected throughout (uptime
  unchanged before/after).

## P4 Completion Notes

Implemented per the approved plan and its 4 corrections. `rule_engine.py` was not modified
at all in P4 — retrieval is wired entirely as post-processing in `job_runner.py`, after
`evaluate_clauses` has already produced final findings.

- **Embedding-model spike (correction #2 — do not silently replace E5):** confirmed live
  against the running Docker Ollama container that `qllama/multilingual-e5-small` — a
  community GGUF quantization of the MIT-licensed `intfloat/multilingual-e5-small` already
  accepted in ADR-005/D-04 — pulls and serves cleanly (131MB) and returns deterministic
  384-dimension embeddings via `/api/embeddings`. **Spike passed; no fallback substitution
  was needed.** `intfloat/multilingual-e5-small` itself was never replaced — this is the same
  MIT-licensed model, just the GGUF artifact required to run it through this project's
  existing Docker-Ollama-only infrastructure (the raw HF repo is not GGUF and Ollama's
  `hf.co/` pull path rejected it directly; searched and found the community re-packaging via
  `WebSearch`, verified it end to end before adopting it — same spike discipline as P1's
  Docling rejection and P3's Haystack go-decision).
- **Qdrant is genuinely queried, not bypassed (correction #1 — must not become "JSON lookup
  only"):** `backend/app/services/guidance_retrieval.GuidanceService` always issues a real
  Qdrant `query_points` call (vector search plus a `rule_id` payload filter) for every
  triggered rule, computing the query vector from a real local embedding of the rule's
  `trigger` text. If the embedding model is unreachable but Qdrant answers, it falls back to
  an unranked `scroll` — still a real Qdrant query, never an in-process dict lookup. Only a
  genuinely unreachable Qdrant degrades the whole batch to `retrieval_mode:
  degraded_full_rules` with `guidance: []` on every finding.
- **User-facing label (correction #3):** the raw `retrieval_mode` enum
  (`qdrant`/`degraded_full_rules`) stays in the API/schema for provenance, but the frontend
  (`SummaryPanel.tsx`) never renders it directly — it shows "Supplemental guidance available"
  or "Guidance unavailable, rule review unaffected". Covered by a frontend test asserting the
  raw enum string never appears in the rendered page.
- **Schema change and Docker volume reset (correction #4):** added `Finding.guidance_json`
  (SQLite `Text`, default `"[]"`) in `backend/app/db/models.py`. There is no migration
  tooling in this prototype (same as every prior phase's DB changes — see P1/P2 notes above);
  an existing SQLite volume created before this change does not have the new column and
  queries against it will fail. **`docker compose down -v` (or equivalently deleting the
  `legal-contract-review-ai_backend_data` volume) is required after pulling P4** before
  bringing the stack back up, exactly as the P2 precedent documented in `AGENT_HANDOFF.md`.
  This was performed before P4's own docker-compose validation below.
- **New modules:** `backend/app/playbook/guidance_loader.py` (validates every guidance
  `rule_id` against the live playbook, mirroring `playbook/loader.py`'s pattern),
  `backend/app/services/embedding_client.py` (thin `httpx` wrapper around Ollama's
  `/api/embeddings`), `backend/app/services/guidance_retrieval.py` (`GuidanceService`, lazy
  Qdrant/embedder construction — never touches either at import time, same lazy-construction
  discipline as P3's `ClauseIntelligenceService`), `backend/scripts/index_guidance.py`
  (embeds and upserts `playbooks/guidance-v1.json` into Qdrant; idempotent, safe to re-run).
- **Authored content:** `playbooks/guidance-v1.json` — 27 illustrative guidance items, one
  per playbook rule, carrying the same "illustrative decision-support, not legal advice"
  disclaimer as `DEFENSE_PLAYBOOK_TEMPLATE.md`. No contract content is ever embedded or
  stored in Qdrant — only this authored corpus.
- **Docker Compose:** new `qdrant` service (official `qdrant/qdrant`, Apache-2.0) behind a
  new opt-in `retrieval` Compose profile. The `ollama` service is shared by P3/P4 and, after
  the P8 follow-up, starts with the default local stack so Admin "Test connection" survives
  laptop/Docker restarts. **No host port is published for Qdrant** —
  tighter than Ollama's setup, per `SECURITY_AND_DATA.md`'s "never expose its port publicly";
  `backend` and `index_guidance.py` (run inside the backend container) reach it only over the
  internal Compose network. Default `docker compose up` includes `backend`, `frontend`, and
  `ollama`; `qdrant` remains excluded unless `--profile retrieval` is used.
- **Dependency:** `qdrant-client>=1.12,<1.13` (Apache-2.0) added to `backend/pyproject.toml`.
- **Tests:** 101 backend pytest cases pass (17 new): `test_guidance_loader.py` (corpus
  validation — every rule_id covered, rejects unknown rule_id/clause_type/category,
  rejects duplicates), `test_guidance_retrieval.py` (`GuidanceService` against fake
  Qdrant/embedder objects — qdrant-mode success, embedding-failure fallback to scroll,
  Qdrant-unreachable degradation, per-rule query deduplication), `test_guidance_attachment.py`
  (the critical proof: `job_runner._attach_guidance` snapshots every risk-relevant Finding
  field before and after retrieval and asserts byte-for-byte equality — guidance retrieval
  structurally cannot alter `rule_id`/`risk_label`/`finding_type`/etc.), plus new assertions
  in `test_reviews_golden_path.py` confirming the real API's degraded-mode response. Frontend:
  2 Vitest cases pass, extended with assertions that the guidance panel renders and the raw
  `degraded_full_rules` string never appears in the UI.
- **Live docker-compose validation (both configurations, same golden fixture):**
  1. Reset the SQLite volume (`docker compose down -v`) for the new `guidance_json` column.
  2. Default mode (`docker compose up -d --build`, no profiles): reproduced the exact
     unchanged 8-rule golden fixture (Critical, `retrieval_mode: degraded_full_rules`,
     `guidance: []` on every finding) — proves P4 introduced zero regression to the default
     path.
  3. Retrieval mode (`docker compose --profile retrieval up -d ollama qdrant`, pulled
     `qllama/multilingual-e5-small`, ran `scripts/index_guidance.py`, rebuilt backend):
     reproduced the same 8 findings with real Qdrant-backed guidance attached
     (`retrieval_mode: qdrant`, real cosine-similarity scores e.g. `0.9395721`).
  4. Directly diffed both API responses in Python: `review_summary` identical;
     findings/missing_clauses identical once `finding_id` and `guidance` are excluded from
     the comparison — this is the live equivalent of the unit-level regression test and the
     concrete proof requested in the approved plan.
  5. Reverted the backend to default mode and confirmed `ai-boardroom-*`/`omniflow-*`
     containers were unaffected throughout (uptime unchanged).

**Follow-up fix (Codex finding, non-blocking):** `GET /api/v1/health/ready` still reported
`vector_store: "not_configured"` even with Qdrant running and retrieval working — a leftover
placeholder from before P4 wired real retrieval. Fixed by adding
`check_qdrant_reachable()` to `guidance_retrieval.py` (a lightweight probe with its own short
1s timeout, independent of `Settings.qdrant_timeout_s` used for real retrieval calls, so
`/health/ready` never hangs when Qdrant is simply absent — the default case) and calling it
from `routes_health.py`. Verified live: `vector_store: "qdrant"` with the `retrieval` profile
running, `vector_store: "not_configured"` with Qdrant stopped, both in ~40ms, and
`status: "ok"` unaffected either way — vector-store readiness never blocks overall
readiness, consistent with retrieval being supplemental-only. 4 new tests (2 in
`test_health.py` exercising the real endpoint with Qdrant absent and a monkeypatched
reachable case, 2 in `test_guidance_retrieval.py` exercising `check_qdrant_reachable`
directly). 105 backend tests pass total.

## P5 Completion Notes

Implemented per the approved plan and its 3 corrections. No cloud adapter was written —
`backend/app/model_adapter/` is unchanged from P3; P5 is UI/API/catalog work only.

- **No real cloud adapter (correction #1):** D-05 (hosted demo model provider) remains `Open`
  in `OPEN_DECISIONS.md`. Anthropic/OpenAI/Gemini are shown in the admin catalog
  (`GET /api/v1/config/providers`) as `implemented: false` — the frontend renders them as
  disabled `<option>`s labelled "(Not enabled)" per `UI_SPEC.md`. No new adapter code was
  written; `ModelAdapter`'s only implementation is still `OllamaAdapter`.
- **Only `ollama` saveable (correction #2):** added `_SAVEABLE_PROVIDERS = {"ollama"}` in
  `routes_config.py`, distinct from `_ALLOWED_PROVIDERS` (the full 4-provider catalog used
  for display). `PUT /config` rejects any `provider_type` not in `_SAVEABLE_PROVIDERS` with
  `CONFIGURATION_INVALID` before touching `_runtime_override` — verified live
  (`curl -X PUT ... -d '{"provider_type":"anthropic"}'` → 400, config unchanged).
- **Reject, not silently ignore (correction #3):** `PUT /config` now validates `base_url`
  independently: rejects it outright if the effective provider isn't `ollama` (cloud base
  URLs are fixed by backend code, per `API_CONTRACT.md`), and rejects malformed URLs (must
  parse with an `http`/`https` scheme and a non-empty hostname) rather than accepting garbage
  or dropping the field silently. Verified live: `base_url: "not-a-valid-url"` → 400 with a
  clear message, both via `curl` and in the browser (inline form error, config unchanged).
  This is a basic scheme/format check only — full DNS/IP-range/egress SSRF hardening (R-07)
  remains explicitly P6 scope, not duplicated here.
- **Backend:** `routes_config.py` gained `_is_valid_http_url()`, the `_SAVEABLE_PROVIDERS`
  split, and `GET /config/providers` (`ProviderInfo` schema: `{provider_type, implemented}`).
  `/config/test` behavior is unchanged from P3 (real Ollama ping, honest
  `PROVIDER_UNAVAILABLE` for anything else) — P5 only added the UI to trigger and display it.
- **Test isolation fix:** `routes_config._runtime_override` is module-level, in-memory-only
  state (D-11) that previously had no reset between tests. Since P5 adds the first tests that
  actually mutate it via `PUT /config`, added an autouse `_reset_config_override` fixture in
  `conftest.py` so config-mutation tests can't leak state into unrelated tests.
- **Frontend:** `AdminModel.tsx` rewritten from a read-only `<dl>` into an editable form —
  provider select (populated from `/config/providers`, disabled options for unimplemented
  providers), model name, base URL (shown only when `provider_type === "ollama"`, per
  `UI_SPEC.md`), a write-only password-type credential field (never pre-filled from
  `GET /config`), Save, and Test connection with a visible success/failure + latency result.
  `api/client.ts`/`api/types.ts` gained `updateConfig`, `getProviders`, `testConfig`,
  `ConfigUpdateRequest`, `ConfigTestResult`, `ProviderInfo`.
- **Tests:** 9 new backend tests (114 total) covering the providers catalog shape, saving a
  valid Ollama config, rejecting an unimplemented provider, rejecting an unknown provider,
  rejecting `base_url` for a non-ollama effective provider (via a monkeypatched
  `Settings.provider_type`, since `ollama` is the only value reachable through the API
  itself), rejecting an invalid/`javascript:` base URL, accepting a valid one, and confirming
  a saved credential value never appears in any response. 6 new frontend tests (8 total)
  covering config rendering, credential never pre-filling, disabled-provider options, a
  successful save, a server-rejected save showing the real error message, and both
  test-connection outcomes.
- **Live verification (real Docker stack, not mocks):** with the `retrieval`/`local-model`
  profiles' Ollama container already running, drove the actual `/admin/model` page in the
  browser — loaded real saved config, clicked "Test connection" and got a genuine
  `Connected to ollama (qwen3:4b) in 14ms` result, submitted an invalid base URL and got the
  real server-side rejection rendered inline, then saved a valid one successfully with no
  console errors. Also confirmed via `curl` directly against the running backend. Full
  `pytest`/`npm run build`/`npm run test` all green; default (no-Ollama) golden-fixture
  smoke test still reproduces the exact unchanged `Critical`/`rule-engine` result, confirming
  P5 didn't disturb the deterministic path. Other local Docker projects
  (`ai-boardroom-*`, `omniflow-*`) confirmed unaffected throughout.
- **No DB/schema changes, no new ports, no new Docker services** — matches the approved plan.

## P6 Completion Notes

Implemented per the approved plan and its 5 corrections. Full factual evidence — commands,
results, dates, limitations — lives in the new `docs/SECURITY_EVIDENCE.md`; this section
summarizes what changed and why.

- **SSRF hardening (correction #1 — explicit allow/block lists, not "private IPs are safe"):**
  `backend/app/services/ssrf_guard.py` is a blocklist-first check: always blocks
  link-local/metadata (incl. `169.254.169.254`)/reserved/multicast/unspecified ranges and
  their IPv6 equivalents; allows private RFC1918 ranges **only** in `deployment_mode: local`
  (rejected in demo mode); always allows `localhost`, `127.0.0.1`, and the Docker Compose
  hostname `ollama`; any other public address passes through (this check targets specific
  dangerous ranges, not a full egress allowlist). Wired into `PUT /config`'s existing
  `base_url` validation, replacing P5's scheme/hostname-only check. 12 new tests.
- **Upload size guard (correction #2 — defense in depth, not a replacement):** added
  `MaxBodySizeMiddleware` (`backend/app/core/middleware.py`), a raw ASGI middleware rejecting
  requests whose `Content-Length` header already exceeds `max_upload_bytes + 1MiB` overhead
  allowance, before Starlette buffers the body. `backend/app/services/upload.py`'s existing
  post-read check (authoritative, since a client can lie about `Content-Length`) is
  explicitly unchanged and still the primary guard. 2 new tests for the middleware; the
  pre-existing post-read oversized-file test is unaffected (the test fixture's size sits
  under the middleware's threshold by design, so it still exercises the post-read path).
- **Log redaction:** `job_runner.py`'s blanket exception handler now logs
  `type(exc).__name__` + `review_id` only, never the exception message/traceback — closes a
  real gap where a `ModelOutputInvalidError` could echo verbatim quoted document evidence
  text into container logs. Verified with a `caplog` test that forces a failure carrying
  fake secret/evidence sentinels and asserts they never appear in captured logs or the API
  response.
- **Retention (correction #4 — lazy delete-on-read, explicit PoC framing):** added
  `Settings.retention_hours_local`/`retention_hours_demo` (default 168h/24h, matching
  `SECURITY_AND_DATA.md`'s existing stated defaults) and a check-on-read in
  `GET /reviews/{id}` — a review past its window is deleted and returns `REVIEW_EXPIRED`
  (410), previously dead code in `errors.py`. No background sweep; `SECURITY_EVIDENCE.md`
  states explicitly this is PoC retention, not production archival — an unread expired
  review stays in SQLite indefinitely. 5 new tests including confirming an in-progress
  review is never expired regardless of `created_at` age, and that the per-review
  `deployment_mode` (not a single global setting) drives which window applies.
- **Qdrant API-key auth (correction #3 — optional/degraded, wired consistently, no
  published port):** `Settings.qdrant_api_key` threaded through all three construction
  sites — `GuidanceService._get_client()`, `check_qdrant_reachable()`, and
  `scripts/index_guidance.py` — via `AsyncQdrantClient(api_key=...)`. **Live testing found a
  real bug before it shipped:** setting `QDRANT__SERVICE__API_KEY` to an *empty string* (the
  naive `${QDRANT_API_KEY:-}` Compose default) makes Qdrant start enforcing auth
  (`401 Must provide an API key`) instead of staying unauthenticated — confirmed by directly
  testing an empty-string-keyed Qdrant container. Fixed two ways: (1) a `field_validator` on
  `Settings.qdrant_api_key` normalizes an empty-string env value to `None`; (2) the `qdrant`
  Compose service deliberately does **not** set that env var by default at all — enabling
  auth requires a documented `docker-compose.override.yml` (see `.env.example`). Verified
  live end to end: default state unauthenticated (200 OK), a real key enforces 401 for
  unauthenticated requests and 200 for authenticated ones. No host port published, unchanged
  from P4. 6 new tests.
- **CORS:** unchanged since P0; added explicit test evidence (disallowed origin gets no
  `Access-Control-Allow-Origin` header, allowed origin does). 2 new tests.
- **Egress-blocked default-mode verification:** reused the `internal: true` Compose network
  override technique from P3, but for a **new, distinct claim**: that the default
  deterministic path (no Ollama, no Qdrant) needs zero outbound network access at all — not
  redoing P3's already-complete Ollama-path verification. Confirmed egress genuinely blocked
  before/during/after, drove the API from inside the backend container (no host port under
  `internal: true`), and diffed the result against a normal-networking baseline run:
  byte-for-byte identical (`Critical` risk, same findings) excluding `review_id`/
  `finding_id`/`completed_at`.
- **Evidence doc (correction #5):** new `docs/SECURITY_EVIDENCE.md` — factual
  command/result/date/limitation entries for all 9 areas above, explicitly stating what P6
  does NOT cover (auth, TLS, rate limiting, SBOM/vuln scanning, full SSRF allowlisting).
- **Tests:** 28 new backend tests (142 total: 12 SSRF, 2 body-size-guard, 1 log-redaction, 5
  retention, 6 Qdrant-auth, 2 CORS); `npm run build`/`npm run test` unchanged (8 frontend
  tests, no frontend code touched in P6). Full live docker-compose validation: default mode
  unchanged golden fixture, egress-blocked default mode identical to baseline, temp-upload
  directory confirmed empty after a real run, port/service inventory confirmed via
  `docker compose config --services`. Other local Docker projects (`ai-boardroom-*`,
  `omniflow-*`) confirmed unaffected throughout (uptime unchanged before/after).
- **No schema changes, no new host ports, ports unchanged (8420/5420/11434, Qdrant still
  unpublished)** — matches the approved plan.

## P7 Completion Notes

Implemented per the approved plan and its 5 corrections. Full factual evidence lives in
`docs/SECURITY_EVIDENCE.md` section 10; this section summarizes what changed and why.

- **Render persistence caveat (correction #1):** `render.yaml` uses Render's **free** Web
  Service plan by default, which does not support a persistent disk. SQLite therefore lives
  on ephemeral container storage — explicitly documented in `render.yaml`'s header comment,
  `docs/OPEN_DECISIONS.md` D-07, and `SECURITY_EVIDENCE.md` §10, not silently accepted as
  production-equivalent. The upgrade path (paid plan + mounted disk, or Render Postgres) is
  documented but **not adopted** for this PoC — no paid-disk approval was given.
- **D-07 (correction #2):** accepted as Render, Docker Web Service
  (`backend/Dockerfile.hosted`, `render.yaml`), persistence explicitly marked ephemeral per
  the caveat above.
- **D-05 (correction #3):** stays open. The hosted demo is deterministic-only — no
  `PART2_PROVIDER_TYPE`/`PART2_OLLAMA_BASE_URL`/`PART2_QDRANT_URL` are set anywhere in the
  hosted config, so there is no model provider or vector store reachable from the hosted
  environment at all. No cloud model adapter was implemented.
- **Admin config lock (correction #4):** `/admin/model` remains visible in the frontend nav
  for demo transparency, **but** `PUT /config`
  (`backend/app/api/routes_config.py`) unconditionally rejects with `CONFIGURATION_INVALID`
  in demo mode regardless of payload — a backend lock, not reliance on UI hiding.
  Verified both via automated tests and a direct authenticated `curl PUT` against the built
  hosted image.
- **Case-study narrative (correction #5):** the persistent, non-dismissible
  `DemoModeBanner` (`frontend/src/components/DemoModeBadge.tsx`) states both the
  synthetic-data warning and "this hosted URL is a synthetic demo convenience... not the
  target production architecture... fully on-premises," shown on every screen in demo mode.
  The same disclaimer is echoed in `README.md`, `docs/DEMO_RUNBOOK.md`, and ADR-012.
- **Hosted-demo access control:** new `DemoBasicAuthMiddleware`
  (`backend/app/core/middleware.py`), outermost middleware, active only when
  `deployment_mode: demo`; fails closed (`503`) if credentials are unconfigured rather than
  serving unauthenticated; `/health/live` stays exempt for the hosting platform's own process
  check. Credentials come from `PART2_DEMO_ACCESS_USERNAME`/`PART2_DEMO_ACCESS_PASSWORD`,
  set only via the Render dashboard, never committed.
- **Same-origin deployment shape:** `backend/Dockerfile.hosted` is a new multi-stage build —
  builds the frontend, copies the static output into the backend image at `/app/static` —
  and `app/main.py` adds a catch-all SPA-fallback route (registered after the API routers)
  that serves it, with an `index.html` fallback so client-side routes resolve on a hard
  refresh. This is additive only: `backend/Dockerfile`, `docker-compose.yml`, and local ports
  are completely untouched — confirmed via `docker compose config` (ports still 8420/5420)
  and a live default-stack smoke test (`GET /health/ready` and `GET /config` both `200`, no
  auth required, matching pre-P7 behavior).
- **Verification performed:** built `backend/Dockerfile.hosted` locally with `docker build`
  and ran it with `docker run`, then verified via `curl`: `/health/live` reachable without
  credentials; `/config` returns `401` without auth and `200` with correct Basic Auth;
  authenticated `PUT /config` still rejected in demo mode; `/` and a client-side route
  (`/reviews/abc`) both serve the built frontend correctly. Full detail and exact commands in
  `SECURITY_EVIDENCE.md` §10.
- **Tests:** 7 new backend tests (149 total: 6 `test_demo_access.py`, 1
  `test_update_config_rejected_unconditionally_in_demo_mode`); 2 new frontend tests (10
  total: `demo-mode.test.tsx`, banner/on-prem-disclaimer shown and full nav visible in demo
  mode, no banner in local mode). Full backend
  (`python -m pytest -q`) and frontend (`npm run build`, `npm run test -- --run`) suites
  green.
- **Deferred, not a P7 gap (explicit user decision on review):** the actual live Render
  deployment — creating the Render service, setting the two demo-access env vars in its
  dashboard, and obtaining a real public URL — is deferred to a later polish/optimization
  phase, not required for P7 acceptance. All packaging needed for it is committed
  (`render.yaml`, `backend/Dockerfile.hosted`); whoever picks up that later phase runs it and
  fills in `docs/DEMO_RUNBOOK.md`'s remaining `TBD` fields (hosted URL, generated fixture
  artifact) afterward. Dependency/container vulnerability
  scan, SBOM, and secret scan also remain not done (already disclosed since P6, still out of
  scope here).

## P8.1 Completion Notes (Dashboard API)

Implemented per the approved proposal and Codex's 2 corrections.

- **`GET /api/v1/reviews`** added to `backend/app/api/routes_reviews.py`, declared before
  `GET /{review_id}` (explicit route-order correction). Summary-only: never returns
  `evidence_text`, full `findings`/`missing_clauses`, `parsed_text`, or model/credential
  internals — verified by a dedicated negative-assertion test.
- **Retention shared, not duplicated (correction: reuse, not reimplement):** extracted the
  existing P6 `_retention_hours_for`/`_is_expired` logic out of `routes_reviews.py` into
  `backend/app/services/retention.py` as `retention_hours_for`/`is_expired`, with zero
  behavior change (full suite re-run green before adding any new code). Both the single-GET
  and the new list route now call the same functions. **Delete-on-encounter for expired
  terminal reviews** (approved design choice) — the list endpoint deletes any expired row it
  fetches on a page and excludes it from the response, matching `GET /{review_id}`'s existing
  lazy delete-on-read precedent; a returned page may therefore contain fewer than `limit`
  items when this happens (documented in `API_CONTRACT.md`).
- **`ReviewRepository.list_summaries()` returns `list[tuple[Review, int, int, int]]`**
  (correction: DTO/tuple per row, not bare `list[Review]`) — one page query
  (`ORDER BY created_at DESC LIMIT/OFFSET`) plus one grouped aggregate query against
  `Finding` (`func.count`/`func.sum(case(...))` keyed by `review_id`), regardless of page
  size up to `limit=50`. Aggregate semantics verified identical to the existing
  `_build_review_out` counting logic via a test comparing the list item's counts against the
  same review's single-GET `review_summary`.
- **Schemas:** added `ReviewSummaryItem`/`ReviewListOut` to `backend/app/schemas/review.py`
  (additive only — no changes to `ReviewOut`/`ReviewSummary`/any existing response model).
  `limit`/`offset` validated via FastAPI `Query(default=20, ge=1, le=50)` /
  `Query(default=0, ge=0)`; `limit=51` returns `422`.
- **No schema migration** — `list_summaries()` reads existing `Review`/`Finding` columns
  only. **No frontend changes** — backend-only, confirmed via unaffected `npm run build`/
  `npm run test`. **No rule/model/retrieval changes** — `rule_engine.py`, model adapters, and
  `guidance_retrieval.py` untouched.
- **Tests:** 9 new tests in `backend/tests/test_reviews_list.py` (empty list, ordering,
  limit/offset, limit-over-max rejection, aggregate-count parity with single-GET, zeroed
  counts for non-completed reviews, expired-review absence-and-deletion, payload exclusion
  of evidence/full findings, demo-mode Basic Auth gating). Full backend suite: **158 passed**
  (149 + 9 new, zero regressions from the retention-helper extraction).
- **Live verification:** ran `GET /api/v1/reviews?limit=5` against the running Docker stack
  (`legal-contract-review-ai-backend-1`, hot-reloaded via the existing bind-mounted
  `--reload` uvicorn setup) — confirmed real newest-first review history with correct
  aggregate counts and no leaked evidence/document text, matching the automated test
  assertions.
- **Demo-mode gating:** automatically covered by P7's blanket `DemoBasicAuthMiddleware`, no
  route-specific auth code needed — verified with one test.
- Full detail: `docs/API_CONTRACT.md` (new `GET /api/v1/reviews` section),
  `docs/OUTPUT_SCHEMA.md` (new summary-list item shape), `docs/SECURITY_AND_DATA.md` (P8.1
  retention note), `docs/IMPLEMENTATION_BACKLOG.md` (P8 checklist items checked off).

## P8.2 Completion Notes (Brand and Shell)

Implemented per the approved proposal, with Codex's 1 doc correction applied.

- **Favicon replaced:** `frontend/public/favicon.svg` now a document/checkmark glyph (navy
  fill, gold checkmark accent), replacing the previous unrelated abstract purple-blob mark
  left over from the original scaffold. Reused as the header wordmark icon
  (`App.tsx`'s `.brand-mark`, via `<img src="/favicon.svg">`) rather than a separate asset.
- **Unused scaffold asset deleted:** `frontend/public/icons.svg` (confirmed unreferenced
  anywhere in `frontend/src/` or `index.html` via grep before deletion).
- **Palette:** `frontend/src/index.css` `:root` (and its `prefers-color-scheme: dark`
  override) now define `--navy`/`--gold` and repoint `--accent` at `--navy`, matching the
  navy/gold visual language already used in the Part 1/Part 3 case-study artifacts.
  **`--risk-*` and the demo-mode warning colors (`badge-demo`/`demo-banner`) are
  deliberately unchanged** — those are semantic/warning colors, not brand colors. Gold is
  used only as a non-text accent (active-nav underline, focus outline) to avoid a WCAG
  contrast failure that gold-as-text-color would cause.
- **Typography:** font stack changed to `"Aptos", "Helvetica Neue", Arial, system-ui,
  sans-serif`, matching Part 1/Part 3.
- **Shell:** header gets a navy bottom border, wordmark + product name lockup, gold
  active/hover nav underline; footer lightly restyled; new `:focus-visible` outline styles
  (previously absent — a real accessibility gap, now closed) for keyboard navigation; a
  mobile breakpoint added so the header/nav wraps cleanly under 640px instead of
  overflowing next to the demo badge.
- **Nav unchanged (doc-corrected before implementation):** stays `New review` +
  conditional `Admin` only. No `Dashboard` link was added — that route is P8.3's, and a
  link to a route that doesn't exist yet would look broken. The shell is visually ready to
  receive it once P8.3 ships.
- **No route changes:** `/` still redirects to `/review/new`, confirmed unchanged in
  `App.tsx`. **No backend changes.** **No markup changes** to `ReviewNew.tsx`,
  `ReviewStatus.tsx`, `AdminModel.tsx`, `FindingCard.tsx`, `FindingsList.tsx`,
  `StageProgress.tsx`, `SummaryPanel.tsx`, `UploadForm.tsx`, or `DemoModeBadge.tsx` — their
  colors shift only via the shared CSS variables, as anticipated in the approved proposal.
- **Verification:** `npm run test -- --run` — 10/10 pass, no test edits needed (exact nav
  label text and demo-banner copy preserved, satisfying `demo-mode.test.tsx`'s assertions
  unchanged). `npm run build` — clean. Rebuilt and ran the hosted-image-adjacent local
  Docker frontend container (`docker compose up -d --build frontend`) since
  `frontend/public/` isn't bind-mounted in `docker-compose.yml` (only `src/` and
  `index.html` are) — confirmed via browser screenshot in light mode, dark mode, desktop
  width, and mobile width (375px): new favicon/wordmark renders, active-nav gold underline
  works, header wraps correctly on mobile with no overflow, Admin page (local mode) renders
  with the new palette applied via shared tokens with no visual regression.
- Full detail: `docs/UI_SPEC.md` (P8.2 shell note), `docs/P8_UI_UX_POLISH_PLAN.md` (P8.2 row
  and status flipped to complete, with the nav-wording correction applied).

## P8.3 Completion Notes (Dashboard/Home)

Implemented per the approved proposal, exactly matching all stated guardrails.

- **New `Dashboard` page** (`frontend/src/pages/Dashboard.tsx`) fetches
  `GET /api/v1/reviews?limit=50` once on mount (no auto-polling — a static snapshot is
  honest and sufficient for this phase) via a new `listReviews()` client method
  (`frontend/src/api/client.ts`) and matching `ReviewSummaryItem`/`ReviewListOut` types
  (`frontend/src/api/types.ts`, mirroring the backend P8.1 schema exactly). **No backend
  changes** — the P8.1 API already carried everything needed; no gap was found.
- **`/` now renders `Dashboard`** instead of redirecting to `/review/new`
  (`App.tsx`'s `<Route path="/" element={<Navigate .../>} />` replaced with
  `<Route path="/" element={<Dashboard />} />`). `/review/new` is completely unchanged.
- **`Dashboard` added as the first nav item** (`<NavLink to="/" end>`). The full nav
  (`Dashboard`, `New review`, `Architecture`, `Playbook`, `Admin`) is visible in demo mode
  so evaluators can inspect the complete product surface; backend locks still prevent
  configuration writes in demo mode.
- **Metrics are strictly real and honestly scoped, per the approved guardrails:**
  - "Reviews shown" is always phrased "N (up to 50 most recently retained)" — never "Total
    reviews" or "All reviews", since P6's retention policy actively deletes older rows and
    the API caps at `limit=50`.
  - Completed / In progress / Failed counts computed from `status` directly.
  - Risk distribution (Critical/High/Medium/Low) computed from `overall_risk` among
    completed items only.
  - Retrieval mode split (qdrant vs. degraded) computed from `retrieval_mode` among
    completed items only (non-completed rows carry a not-yet-meaningful DB default and are
    excluded to avoid misleading noise).
  - **No fake ROI, time-saved, money-saved, or "risks prevented" claims anywhere** — and no
    summed "total findings caught" headline stat either, deliberately excluded since it
    would read as an implied value pitch even though it's real, derivable data.
- **Recent Reviews table**: up to 10 most recent (client-side slice of the fetched 50,
  sorted by `created_at` desc), semantic `<table>` markup, each "View" link to the existing
  `/reviews/{id}` route (no new page) carries a per-row accessible name
  (`aria-label="View review for {document_name}"`) so multiple identical "View" link texts
  are distinguishable to screen readers — confirmed via `read_page` in the live browser
  check. Table wrapped in its own `overflow-x: auto` container so it scrolls independently
  on narrow viewports instead of causing page-wide horizontal scroll.
- **Empty state**: "No reviews yet. Start your first contract review." + CTA, not an error
  — a normal, expected state for a fresh instance.
- **Loading/error states** mirror the established `ReviewStatus.tsx` pattern exactly
  (`ApiRequestError` → `role="alert"` with the real message; generic fallback otherwise).
- **Tests:** 7 new tests in `frontend/tests/dashboard.test.tsx` — loading, API error,
  empty state, computed-stats-and-table-rendering with explicit negative assertions that no
  "Total reviews"/"All reviews"/"hours saved"/"money saved"/"risk(s) prevented"/"ROI" text
  ever appears, full nav visible in both local and demo mode, and root route `/` rendering
  Dashboard content instead of redirecting.
  Full frontend suite: **17 passed** (10 existing + 7 new, zero regressions).
- **Verification:** `npm run test -- --run` 17/17 pass; `npm run build` clean; backend
  suite re-run unaffected (**158/158**, confirming zero backend touch as required). Live
  browser check against the running Docker stack's real review history (hot-reloaded, no
  rebuild needed since `frontend/src/` is bind-mounted): light mode, dark mode, desktop, and
  mobile (375px) all verified — real counts (12 reviews shown, 12 completed, correct risk
  distribution, correct retrieval split), recent-reviews table renders with working,
  correctly-hrefed View links, table scrolls horizontally on its own on mobile without
  page overflow, and navigating directly to a review from the dashboard's data confirmed the
  existing findings screen still renders correctly with the P8.2 palette applied.
- Full detail: `docs/UI_SPEC.md` (P8.3 Dashboard/Home section),
  `docs/P8_UI_UX_POLISH_PLAN.md` (P8.3 row flipped to complete).

## P8.4 Completion Notes (Upload Screen Polish)
- **Scope:** frontend-only, no backend/rule/model/retrieval changes — no blocker was found
  that required one.
- **`frontend/src/pages/ReviewNew.tsx`:** restyled from a bare "Start a contract review" page
  into `New Legal Review` with a one-line pipeline lede; a page-level "Active playbook"
  summary card (`role="region"`, `aria-label="Active playbook summary"`) showing the playbook
  id (`defense-services-v1`), version (`1.0-draft`), rule count (`27`, hardcoded static
  display text — reused from the already-verified P8.1-era playbook fact check, not a new
  backend endpoint since this is static per-playbook data, not per-review data), the 8
  required clause families in plain language, and a "Produces:" line listing the finding
  output shape (deviation flags, missing clauses, risk labels, evidence, recommended
  actions — a description of the output schema, not a performance claim); a 5-stage
  `workflow-strip` (Upload → Parse → Extract clauses → Apply playbook → Structured findings);
  and a hosting-neutral trust note ("Processed on this server and never sent to a public AI
  service.") that deliberately avoids "on-premises"/"on-prem"/"air-gapped" wording since the
  same screen can render in hosted Demo mode.
- **`frontend/src/components/UploadForm.tsx`:** removed the inline `.playbook-info` line
  (superseded by the new page-level card) and the now-unused `playbookId` prop from `Props`
  and the component signature. Upload mechanics — dropzone drag/drop, browse, file-type/size
  validation (`.pdf`/`.docx`, 15 MB), error display, and the submit button — are byte-for-byte
  unchanged, including the exact strings `golden-path.test.tsx` depends on ("Drag and drop a
  contract here...", "Upload a PDF or DOCX file.", "Review contract").
- **`frontend/src/index.css`:** added `.playbook-card`, `.playbook-card-label`,
  `.playbook-clause-list` (2-column), `.trust-note`; removed the now-dead `.playbook-info`
  rules; renamed `.dashboard-workflow` → shared `.workflow-strip` (used by both `ReviewNew`
  and `Dashboard`).
- **`frontend/src/pages/Dashboard.tsx`:** one-line className update
  (`dashboard-workflow` → `workflow-strip`) to match the renamed shared class; no other
  changes.
- **Explicitly declined, per approved scope:** no demo-mode acknowledgement checkbox was
  added (the existing global, non-dismissible `DemoModeBanner` in `App.tsx` already carries
  that disclosure; adding new interactive gating logic was judged out of scope for a
  visual-polish phase and was explicitly called out and confirmed with the user before
  implementation).
- **Tests:** new `frontend/tests/review-new.test.tsx` (5 tests) — playbook card renders the
  real playbook id/version/rule-count/clause-family/output-shape text; the 5-stage workflow
  strip renders; the trust note text is present and negative-asserts against
  "on-premises"/"on-prem"/"air-gapped"; no ROI/hours-saved/money-saved/risks-prevented text
  appears; the protected drag-and-drop label and `Review contract` button are preserved.
  `golden-path.test.tsx` required no changes and still passes unmodified. Full frontend
  suite: **22 passed** (17 existing + 5 new, zero regressions).
- **Verification:** `npm run test -- --run` 22/22 pass; `npm run build` clean; backend suite
  re-run unaffected (**158/158**, confirming zero backend touch). Live browser check against
  the running Docker stack (hot-reloaded via bind-mounted `frontend/src/`, no rebuild
  needed): dark desktop, light desktop, and dark mobile (375px, confirmed
  `document.documentElement.scrollWidth === window.innerWidth`, no horizontal overflow) all
  rendered correctly with no console errors. A live drag-and-drop file upload could not be
  driven through the Browser-pane automation (no file-input-set capability in that tool), so
  the "unchanged upload behavior" claim rests on: (a) the unmodified, passing
  `golden-path.test.tsx`, which exercises the full submit → `createReview` → navigate →
  findings-render path against a mocked API and is unaffected by this change set, and (b) a
  visual/DOM confirmation that the dropzone, file input, hint text, and submit button are
  present and unchanged in the live preview. This is disclosed as a verification-method
  limitation, not a behavior change.
- Full detail: `docs/UI_SPEC.md` (Review Screen P8.4 note), `docs/P8_UI_UX_POLISH_PLAN.md`
  (P8.4 row flipped to complete).

## P8.5 Completion Notes (Findings Screen Polish)
- **Scope:** frontend-only, no backend/rule/model/retrieval/schema changes — no blocker was
  found that required one.
- **`frontend/src/pages/ReviewStatus.tsx`:** added `<h1>Review result</h1>` and a compliance
  banner (`.findings-disclaimer`) in the completed-review branch only, with the exact
  approved copy: "Findings are decision support only, not legal advice. Final risk labels
  are assigned by the deterministic playbook rule engine. Supplemental guidance, when shown,
  is illustrative context only and does not change any finding's risk label." Polling
  (`useEffect`/`getReview`/`setTimeout`), the loading/failed/in-progress branches, and the
  route path are all unchanged.
- **`frontend/src/components/SummaryPanel.tsx`:** the flat `.summary-counts` `<ul>` was
  split into a "Findings by severity" group (Critical/High/Medium/Low, unchanged numbers)
  and a separate callout row for "Missing clauses"/"Needs review" — same
  `review_summary` fields, no data removed, purely a markup/CSS restructure.
- **`frontend/src/components/FindingsList.tsx`:** the existing severity/clause-type/
  low-compliant filter state and the `visible` filtering logic are byte-for-byte unchanged.
  Only the *rendering* of `visible` changed: it's now split into
  `visibleDeviations`/`visibleMissingClauses` by `finding_type`, and `visibleDeviations` is
  rendered under per-severity `<h2>` subheadings (`Critical (n)`, `High (n)`, etc., only
  non-empty groups render) followed by a separate "Missing clauses (n)" section. The
  `Filters` panel got a heading; its inputs and `onChange` handlers are unchanged.
- **`frontend/src/components/FindingCard.tsx`:** added `.field-label` captions ("Evidence",
  "Why this is flagged", "Recommended action") above the existing evidence/reason/action
  blocks — the underlying text content is unchanged (the previous inline `<strong>Recommended
  action:</strong>` prefix was replaced by the new label, not duplicated). The guidance
  panel's `<summary>`/disclaimer/list markup and copy are **completely unchanged**; only its
  container CSS gained a border/background so it reads as visually distinct from the
  finding's rule-derived content.
- **`frontend/src/index.css`:** new `.findings-disclaimer`, `.summary-stats-group`,
  `.summary-stats-label`, `.summary-counts-callout`, `.filters-heading`, `.severity-group`,
  `.severity-group-heading`, `.severity-group-count`, `.missing-clauses-section`,
  `.finding-field`, `.field-label` rules; `.guidance-panel` restyled to a bordered/tinted
  container (copy untouched).
- **Tests:** new `frontend/tests/findings-screen.test.tsx` (4 tests, rendering `ReviewStatus`
  against a mocked `getReview` with 2 deviation findings across 2 severities plus 1 missing
  clause) — compliance banner shows all three required claims; findings are grouped under
  the correct severity headings and missing clauses render in their own section, not mixed
  in; evidence/reasoning/recommendation field labels render without losing any finding
  content; the page `h1` and the missing-clause/needs-review counts are present.
  `golden-path.test.tsx` required **zero changes** and still passes unmodified against the
  new markup. Full frontend suite: **26 passed** (22 existing + 4 new, zero regressions).
- **Verification:** `npm run test -- --run` 26/26 pass; `npm run build` clean; backend suite
  re-run unaffected (**158/158**, confirming zero backend touch). Live browser check against
  the running Docker stack (hot-reloaded via bind-mounted `frontend/src/`, no rebuild
  needed): navigated directly to a real completed review
  (`sentinel-support-agreement.pdf`, 8 findings across Critical/High/Low + 1 missing clause)
  fetched live from `GET /api/v1/reviews`. Confirmed the compliance banner, severity-grouped
  headings (`Critical (1)`, `High (4)` visible with the default filter set, `Missing clauses
  (1)`), field labels, and every finding's rule ID/evidence/reasoning/recommendation/source/
  confidence rendered with no data loss, in dark mobile (375px, no horizontal overflow) and
  light desktop, with no console errors.
- Full detail: `docs/UI_SPEC.md` (Findings Screen P8.5 note), `docs/P8_UI_UX_POLISH_PLAN.md`
  (P8.5 row flipped to complete).

## P8.6 Completion Notes (Admin Screen Polish)
- **Scope:** frontend-only, no backend/config-provider/schema changes — no blocker was found
  that required one. Existing API calls remain `GET /config`, `GET /config/providers`,
  `PUT /config`, and `POST /config/test`.
- **`frontend/src/pages/AdminModel.tsx`:** restyled `/admin/model` into a clearer enterprise
  runtime-provider configuration screen. Added a `Runtime Provider Configuration` heading
  and lede stating this is provider orchestration for the structured review pipeline, not a
  chatbot setting; added posture cards for deterministic rule-engine authority, Docker
  Ollama/local runtime path, and hosted-provider placeholders; added a current-config
  summary card; added a provider catalog showing enabled/disabled status; added security
  notes and a connection-test panel. The original form controls, provider select, model
  field, Ollama base URL field, write-only credential field, Save, and Test connection
  behavior are preserved.
- **Provider-status guardrail:** Ollama remains the only enabled/saveable provider. Anthropic,
  OpenAI, and Gemini are shown as disabled placeholders only; the screen explicitly states
  D-05 remains open and no cloud adapter is enabled by the UI.
- **Security guardrail:** credentials remain write-only and are never pre-filled or displayed
  after save. The connection test is labelled as a reachability check only and explicitly
  does not run a review or expose credentials. Demo-mode copy states production
  configuration changes remain server-side locked and admin-entered credentials clear on
  service restart.
- **`frontend/src/index.css`:** added scoped admin card/catalog/security/connection-panel
  styles using the existing navy/gold palette and semantic status colors.
- **Tests:** expanded `frontend/tests/admin-model.test.tsx` from 6 to 8 tests. New/updated
  assertions cover the runtime-configuration/chabot distinction, rule-engine authority
  wording, D-05/open-cloud-adapter wording, disabled-provider catalog status, safe credential
  display, reachability-only connection-test wording, and demo-mode lock copy. Full frontend
  suite: **28 passed** (26 existing + 2 net new, zero regressions).
- **Verification:** `npm run test -- --run` 28/28 pass; `npm run build` clean. Backend suite
  will be rerun as part of the P8.6 final validation gate, but no backend files were edited.
- Full detail: `docs/UI_SPEC.md` (Admin Model Screen P8.6 note),
  `docs/P8_UI_UX_POLISH_PLAN.md` (P8.6 row flipped to complete).

## P8.7 Completion Notes (Documentation and Final Validation)
- **Scope:** final P8 reconciliation and validation only. No feature, rule, model, retrieval,
  schema, hosting, or PDF/export changes were made in P8.7.
- **Documentation reconciliation:** P8 status was updated to `complete` in
  `docs/P8_UI_UX_POLISH_PLAN.md`, `docs/IMPLEMENTATION_PHASE_PLAN.md`,
  `docs/IMPLEMENTATION_BACKLOG.md`, `docs/PLAN.md`, `docs/AGENT_HANDOFF.md`, and
  `docs/MASTER_INDEX.md`. P8.1-P8.7 are now consistently marked complete; hosting/live URL
  and PDF/export remain explicitly out of scope for P8.
- **Validation evidence:** frontend suite passed (**28/28**); frontend production build passed;
  backend suite passed (**158/158**, rerun outside the sandbox because mocked Ollama tests bind
  a local HTTP socket); Docker Compose reported backend/frontend containers up on ports
  **8420/5420**; backend readiness returned `{"status":"ok",...}`; frontend returned HTTP
  200.
- **Live smoke evidence:** uploaded `fixtures/sentinel-support-agreement.pdf` to the running
  backend at `POST /api/v1/reviews`; the review completed with `overall_risk: Critical`, **7
  deviation findings**, and **1 missing clause**. This confirms the P8 UI polish did not break
  the underlying upload-to-findings workflow.
- **Exit position:** P8 is ready for user browser review. Remaining deferred work is outside
  P8: live public URL deployment and PDF/export packaging.

## P8.8 Completion Notes (Admin Playbook Viewer)
- **Scope:** read-only playbook visibility requested after P8.7. CRUD was deliberately not
  implemented because editing/removing playbook rules changes legal risk decisions and would
  require versioning, validation, audit trail, rollback, and explicit approval.
- **Backend:** added `GET /api/v1/playbooks/active` (`backend/app/api/routes_playbooks.py`)
  and typed response models (`PlaybookOut`, `PlaybookRuleOut`, `PlaybookClauseFamilyOut`).
  The endpoint loads the active `defense-services-v1` playbook through the existing loader
  and returns a UI-safe view: playbook id/version, editable=false, edit policy, clause
  families, missing-clause mappings, and all 27 rules. It does not expose file paths, loader
  internals, credentials, prompts, or document content.
- **Frontend:** added `/admin/playbook` (`frontend/src/pages/AdminPlaybook.tsx`) and a
  local-mode `Playbook` nav link. The page shows overview metrics, severity coverage,
  required clause-family cards, missing-clause rule ids, and a full responsive rule catalogue. It is hidden
  in hosted Demo mode with the existing Admin/configuration navigation.
- **Behavior guardrail:** no rule engine, playbook JSON, model adapter, retrieval logic,
  upload workflow, or review-result schema was changed.
- **Tests:** added `backend/tests/test_playbooks_api.py` (3 tests) and
  `frontend/tests/admin-playbook.test.tsx` (5 tests). Validation after implementation:
  backend 163/163 passed, frontend 33/33 passed, frontend build clean.

## P9 Completion Notes (Case-Study Alignment)
- **P9.1 Architecture/Stack/Data Flow:** added `/architecture` and `Architecture` nav. The
  page explains React/Vite, FastAPI, Haystack, Ollama-compatible model runtime, Qdrant,
  SQLite, pypdf/python-docx, deterministic playbook authority, secure data-flow steps, and
  trust boundaries. It is visible in local and demo modes and exposes no secrets. Targeted
  validation: `frontend/tests/architecture.test.tsx` passed and frontend build passed.
- **P9.2 Approved-Template Drafting Support:** added `backend/app/services/drafting.py`,
  `suggested_draft_clause` response schema, API serialization, and a collapsed
  `Suggested approved clause language` panel in `FindingCard`. Drafting is deterministic
  template language keyed by `rule_id`, not free-form generation; every panel says Legal
  approval is required. Targeted validation: backend golden-path tests passed and frontend
  findings/golden-path tests passed.
- **P9.3 Qdrant Guidance Visibility:** dashboard now shows Qdrant guidance coverage as an
  operating-mode card; completed review pages show `Qdrant supplemental guidance active` or
  `Qdrant guidance unavailable` with explicit "rule review unaffected" copy. Raw enum
  values such as `degraded_full_rules` remain hidden from users. Targeted validation:
  dashboard/findings/architecture frontend tests passed and build passed.
- **Behavior guardrail:** no rule-engine predicates, risk aggregation, playbook JSON,
  model-adapter behavior, or Qdrant retrieval behavior changed.
- **Final validation:** backend suite **163/163 passed** (rerun with local socket binding
  permission for mocked Ollama tests); frontend suite **38/38 passed**; frontend production
  build clean; Docker Compose rebuilt backend/frontend on **8420/5420**; live upload of
  `fixtures/sentinel-support-agreement.pdf` completed with `mode_requested: model`,
  `mode_used: model`, `fallback_used: false`, `overall_risk: Critical`,
  `retrieval_mode: degraded_full_rules`, and approved-template draft support on all returned
  finding/missing-clause items.

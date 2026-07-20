# Part 2 Test and Acceptance Plan

## Golden-Path Test
Upload the contract defined in `DEMO_FIXTURE_SPEC.md`. The system must complete the pipeline, match the required expected rule outcomes, resist the embedded prompt-injection sentence, and display a structured result matching `OUTPUT_SCHEMA.md`.

## Functional Tests
Status markers below reflect P1 (real parsing); P2+ replace the fixed-fixture findings path.

- [x] PDF upload succeeds. (P1: real `pypdf` extraction)
- [x] DOCX upload succeeds. (P1: real `python-docx` extraction)
- [x] Unsupported and oversized files are rejected safely. (P0/P1)
- [x] Encrypted documents fail with `ENCRYPTED_DOCUMENT`. (P1) Documents over 100 pages fail
  with `DOCUMENT_TOO_LONG`. (P1; DOCX page count is a word-count estimate, see `DATA_MODEL.md`)
- [x] Empty or image-only documents with no usable text fail with `NO_REVIEWABLE_TEXT` and no
  findings. (P1)
- [x] Non-contract or out-of-scope documents fail with `DOCUMENT_NOT_APPLICABLE` and no
  findings. (P3: real classification-based check — applicable if >= 2 required clause types
  classify at >= 0.60 confidence; source-agnostic, runs identically for both the
  deterministic and model-assisted extraction paths. Accuracy is still bounded by whichever
  path produced the classification. See `WORKFLOW_SPEC.md`'s P3 stage-order correction.)
- In-progress responses use only the documented status and `current_stage` values.
- [x] Clauses include evidence text and section references where available. (P2)
- [x] Each finding maps to a playbook rule. (P2)
- [x] Missing required clauses are reported separately. (P2)
- [x] Overall risk is derived from findings using a documented rule. (P2: max-severity, no averaging)
- [x] Summary counts equal the findings returned. (P2)
- Terminal review records do not change after refresh.
- Active jobs interrupted by a PoC backend restart recover as `failed` with `JOB_INTERRUPTED`, not as permanently active jobs.
- API output passes schema validation.
- Findings UI displays all required output fields.
- [x] Configuration UI never displays a saved API key. (P5: credential field is write-only,
  never pre-filled from `GET /config`; verified by test that a submitted credential value
  never appears in any response body.)
- [x] Admin-entered credentials are absent from SQLite, logs, API responses, and review
  results, and the in-memory override clears on restart. (Unchanged since P0/D-11 —
  `_runtime_override` holds only a boolean `has_credential` flag, never the raw value.)
- [x] Ollama and cloud configurations use the same internal model interface. (P3:
  `ModelAdapter` protocol in `backend/app/model_adapter/base.py`; only `OllamaAdapter` is
  implemented, cloud adapters remain unimplemented behind the same interface, P5/D-05)
- [x] Only implemented, server-allowlisted providers can be selected or saved. (P5:
  `PUT /config` rejects any `provider_type` outside `_SAVEABLE_PROVIDERS = {"ollama"}` with
  `CONFIGURATION_INVALID` — verified live via `curl` and in the browser; `/config/test`
  returns `PROVIDER_UNAVAILABLE` honestly for any non-ollama provider_type, unchanged since
  P3; catalog display via `GET /config/providers` distinguishes "shown" from "saveable".)
- [x] Configurable model endpoint (Ollama `base_url`) rejects malformed input. (P5: basic
  scheme/hostname format check — `CONFIGURATION_INVALID` for non-http(s) schemes, missing
  hostname, or non-Ollama providers submitting a `base_url` at all. P6 adds DNS
  resolution + explicit blocklist for link-local/metadata/reserved/multicast, with private
  RFC1918 ranges gated to local mode — see Security Tests below and `SECURITY_EVIDENCE.md` §1.)
- [x] Supplemental guidance is retrieved and attached to findings without changing any
  risk-relevant field. (P4: verified two ways — a unit test
  (`test_guidance_attachment.py`) that snapshots every risk-relevant `Finding` field
  before/after `_attach_guidance` runs and asserts byte-for-byte equality, and a live
  docker-compose run diffing retrieval-on vs retrieval-off API responses for the same
  document — identical `review_summary`/findings/missing_clauses except `finding_id` and
  `guidance`. See `IMPLEMENTATION_PHASE_PLAN.md` P4 Completion Notes.)
- [x] Retrieval degrades cleanly when Qdrant or the embedding model is unreachable. (P4:
  default `docker compose up` — no Qdrant running — reproduces the exact unchanged golden
  fixture with `retrieval_mode: degraded_full_rules` and `guidance: []` on every finding;
  never fails the review.)
- [x] `GET /api/v1/health/ready` reports real vector-store reachability. (Follow-up fix:
  `dependencies.vector_store` is `"qdrant"` when Qdrant answers, `"not_configured"` when
  unreachable/absent — verified live in both states, ~40ms each; overall `status` is never
  affected by it, since retrieval is supplemental-only.)

## Security Tests
- [x] File names cannot escape the upload directory. (P1: server-generated names only;
  `sanitize_display_name` strips path components — unchanged, re-confirmed in P6 review.)
- [x] Contract text cannot alter pipeline instructions or invoke tools. (P2/P3: adversarial
  fixture test since P2; SYSTEM_INSTRUCTION explicitly forbids following in-document
  instructions, live-verified against the model path in P3.)
- [x] Invalid model JSON does not reach the UI as a successful review. (P3:
  `backend/tests/test_ollama_adapter.py::test_repair_fails_twice_raises_model_output_invalid`
  — one repair attempt, then typed `MODEL_OUTPUT_INVALID` failure, no partial success)
- [x] Secrets and document bodies do not appear in normal logs. (P6:
  `backend/tests/test_log_redaction.py` — forces a failure carrying fake secret/evidence
  sentinels and asserts they never appear in captured logs or the API response;
  `job_runner.py`'s exception handler now logs exception type + review_id only.)
- [x] Configurable endpoints reject unsafe schemes and restricted destinations. (P6:
  `backend/tests/test_ssrf_guard.py` — always rejects link-local/metadata/reserved/
  multicast; private RFC1918 ranges rejected outside local mode; DNS-unresolvable hostnames
  rejected. Not a full enterprise egress-policy allowlist — see `SECURITY_EVIDENCE.md` §1's
  stated limitation; a public IP is allowed by default.)
- [x] CORS is limited to configured origins. (P6: `backend/tests/test_cors.py` — disallowed
  origin gets no `Access-Control-Allow-Origin` header, allowed origin does. Behavior
  unchanged since P0, evidence added.)
- [x] Qdrant is unreachable from the public network. (P4: the `qdrant` Compose service
  publishes no host port at all, opt-in `retrieval` profile only.)
- [x] Qdrant unauthenticated access is optionally rejectable. (P6: API-key auth implemented
  and optional — `backend/tests/test_qdrant_auth.py` plus a live test against a real Qdrant
  container confirming an empty-string key incorrectly enforces auth (a real bug caught
  before shipping) versus a real key correctly enforcing it. See `SECURITY_EVIDENCE.md` §5.)
- [x] Qdrant unavailability records degraded retrieval mode but does not change the fixture's
  rule IDs, severities, or overall risk. (P4: verified live, see Functional Tests above.)
- [x] Local mode completes the fixture with outbound internet blocked after artifacts are
  provisioned. (P6: new, distinct from P3's Ollama-path egress-blocked run — proves the
  *default* deterministic path needs zero outbound access at all. Verified live: identical
  result to a normal-networking baseline. See `SECURITY_EVIDENCE.md` §7.)
- [x] Temporary uploads are deleted after success and failure. (P1: verified by test and by
  manual docker-compose inspection of the container's upload-temp directory; re-confirmed
  live in P6, see `SECURITY_EVIDENCE.md` §9.)
- [x] Hosted review records expire after 24 hours, and explicit deletion removes them. (P6:
  lazy delete-on-read enforces `Settings.retention_hours_demo`/`retention_hours_local`,
  returning `REVIEW_EXPIRED` — `backend/tests/test_retention.py`, 5 tests. Explicitly PoC
  retention, not production archival — no background sweep. P4 correction retained: there
  are no "associated vectors" to expire/delete per review — Qdrant stores only the static,
  shared guidance corpus, never contract-derived data; see `DATA_MODEL.md`.)
- [x] Upload size is enforced even before the request body is fully read. (P6:
  `backend/tests/test_middleware.py` — an oversized `Content-Length` is rejected early;
  `upload.py`'s existing post-read check remains the authoritative guard for requests that
  omit or misreport `Content-Length`.)
- [x] Hosted demo access is credential-gated and fails closed if misconfigured. (P7:
  `backend/tests/test_demo_access.py` — `DemoBasicAuthMiddleware` returns `401` without
  correct Basic Auth credentials and `503` if demo mode is on without credentials configured;
  no-op in local mode; `/health/live` stays reachable for the hosting platform's own process
  check. See `SECURITY_EVIDENCE.md` §10.)
- [x] Configuration cannot be changed in hosted demo mode, even by an authenticated client.
  (P7: `backend/tests/test_health.py::test_update_config_rejected_unconditionally_in_demo_mode`
  — `PUT /config` unconditionally returns `CONFIGURATION_INVALID` when
  `deployment_mode: demo`; a backend lock, not just a hidden admin nav link. See
  `SECURITY_EVIDENCE.md` §10.)
- [x] Hosted frontend/backend have no cross-origin surface. (P7: served same-origin from one
  container — `backend/Dockerfile.hosted` + `app/main.py`'s SPA fallback route; verified by
  running the built hosted image locally and confirming `/`, static assets, and a client-side
  route all resolve `200` through the backend port with no separate frontend origin. See
  `SECURITY_EVIDENCE.md` §10.)

## Repeatability Tests
**Status: satisfied.** Ran `fixtures/sentinel-support-agreement.pdf` three times through the
real API against Docker-based Ollama + `qwen3:4b`, plus a fourth run with genuine Docker
network-level egress blocking. See `IMPLEMENTATION_PHASE_PLAN.md` P3 Live Verification Notes
for full detail, including an adapter fix (`/api/generate` -> `/api/chat` with `think: false`)
required to get a real response instead of an empty one from this reasoning-capable model.

- [x] Run the golden fixture three times with the pinned local model. (3/3 completed, real API)
- [x] At least one run must use the live Docker Ollama/Qwen path with runtime egress blocked; a fixed fixture result cannot satisfy this criterion. (Compose network recreated `internal: true`; confirmed `Network is unreachable` from inside the backend container before/during/after the run, while backend-to-ollama traffic on the same internal network kept working.)
- [x] Rule IDs, severities, missing clauses, and overall risk must match across all runs. (All 4 runs: High risk, findings DATA-002/LIAB-002/SUB-002/TERM-001/TERM-002, missing AUD-001/SEC-004 — identical.)
- Explanation wording may differ and is not used for pass/fail. (Not exercised — findings carry fixed `deviation_reason`/`recommended_action` strings from the playbook, no free-text model explanation field.)
- [x] Record confidence values and result variance for all three runs. (All findings 0.9 confidence in all 4 runs; zero variance at `temperature: 0` on this hardware.)
- [x] Qualify the synthetic fixture only when expected clause classifications are `>= 0.80`, outside the `needs_review` confidence band; otherwise tune the synthetic wording and rerun before acceptance. (All observed confidences were 0.9; `needs_review_count: 0` in every run.)
- Any classification-confidence threshold crossing is a failed model-suitability check, not a reason to substitute the fixed fixture. (No threshold crossing observed. Separately, `qwen3:4b` did not classify confidentiality/IP-ownership clause types present in the fixture text — a disclosed model-quality gap, not a confidence-threshold failure; see `RISK_REGISTER.md` R-03.)
- [x] A dedicated boundary test confirms that a relevant candidate below `0.60` emits `REV-001` and also emits the mapped missing-clause rule when no accepted candidate establishes presence. (P2: `backend/tests/test_rule_engine.py::test_rev_001_boundary_emits_needs_review_and_mapped_missing_clause`, using a synthetic low-confidence snippet since P2 has no model to produce real confidence variance)

## Golden Fixture Assertions
Verified as of P2 via `backend/tests/test_reviews_golden_path.py` (real API upload → rule
engine, PDF and DOCX) — not the fixed-fixture placeholder these assertions were originally
written against:
- [x] Overall risk is `Critical`.
- [x] Findings are exactly `DATA-001`, `CONF-002`, `SUB-001`, `AUD-001`, `IP-002`, `LIAB-001`, `TERM-004`, and `SEC-002`.
- [x] Risk counts are one Critical, five High, zero Medium, and two Low.
- [x] `AUD-001` is the only missing-clause finding.
- [x] No golden-fixture finding has `needs_review: true`.
- [x] The adversarial appendix sentence does not affect classification, rules, severity, or output structure. (`backend/tests/test_rule_engine.py::test_adversarial_sentence_does_not_change_findings`)

Note: these assertions are produced by P2's fixture-oriented deterministic segmentation and
extraction (see `DEFENSE_PLAYBOOK_TEMPLATE.md`), not a general contract parser — passing
against this one committed fixture is not evidence of general contract-review capability.
That is P3 scope.

## Language Tests
- English golden fixture passes all exact assertions.
- Unicode and Indonesian text survive upload, parsing, persistence, API output, and UI rendering without corruption.
- If time permits, a short synthetic Indonesian contract completes as a smoke test; its legal accuracy is not a release claim.

## Demo Acceptance Criteria
- A reviewer can understand the workflow without explanation from the builder.
- One synthetic contract completes end to end from a hosted URL, behind the demo access gate.
- The final evidence pack contains a successful egress-blocked Docker Ollama/Qwen run of the
  same golden fixture, recorded locally (P3/`SECURITY_EVIDENCE.md`); the hosted demo itself is
  deterministic-only (P7, D-05 stays open) and does not run a model live — it is presented as
  a packaging/access convenience, not model-path evidence.
- The live hosted run and local verification run are clearly distinguished from the fixed-result fallback.
- High and Critical findings are visually obvious.
- Evidence and the triggered playbook rule are visible.
- The hosted demo does not expose the admin/config view at all (hidden nav plus backend lock,
  P7); provider portability is instead demonstrated in local mode, where `/admin/model` remains
  fully functional per P5.
- The architecture explanation distinguishes hosted demo processing from the fully on-premises
  target, and every hosted-facing screen/doc states the hosted URL is a synthetic demo
  convenience, not the production on-prem deployment (P7, ADR-012).

## Evidence to Capture
- Screenshot of upload screen
- Screenshot of structured findings
- Screenshot of provider configuration without secrets
- Example API response
- Test command and result
- Deployment URL and health status
- Local-model verification result with egress blocked

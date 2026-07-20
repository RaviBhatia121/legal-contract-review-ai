# Part 2 Master Index

Use this file as the entry point for all Part 2 work.

## Read Order
1. [README.md](../README.md) - current build/run/test entry point
2. [AGENT_HANDOFF.md](./AGENT_HANDOFF.md) - current phase, locked decisions, and next task
3. [PLAN.md](./PLAN.md) - current task list and implementation status
4. [CASE_STUDY_BASELINE.md](./CASE_STUDY_BASELINE.md) - requirements validated against the source PDF
5. [PART2_REQUIREMENTS.md](./PART2_REQUIREMENTS.md) - selected scope and acceptance criteria
6. [OPEN_DECISIONS.md](./OPEN_DECISIONS.md) - accepted defaults and remaining hosted/deployment choices
7. [ARCHITECTURE_DECISIONS.md](./ARCHITECTURE_DECISIONS.md) - accepted technical decisions
8. [TECH_STACK_AND_LICENSES.md](./TECH_STACK_AND_LICENSES.md) - stack selection, licenses, and primary sources
9. [REPOSITORY_STRATEGY.md](./REPOSITORY_STRATEGY.md) - accepted monorepo layout and engineering boundaries
10. [ARCHITECTURE.md](./ARCHITECTURE.md) - components, boundaries, data flow, and deployment modes
11. [NON_FUNCTIONAL_REQUIREMENTS.md](./NON_FUNCTIONAL_REQUIREMENTS.md) - security, reliability, performance, portability, and language targets
12. [SECURITY_AND_DATA.md](./SECURITY_AND_DATA.md) - security, data handling, retention, and deployment controls
13. [DEFENSE_PLAYBOOK_TEMPLATE.md](./DEFENSE_PLAYBOOK_TEMPLATE.md) - versioned review rules for the Legal demo
14. [RULE_EVALUATION_SPEC.md](./RULE_EVALUATION_SPEC.md) - normalized attributes and deterministic rule predicates
15. [MODEL_AND_PIPELINE_CONTRACT.md](./MODEL_AND_PIPELINE_CONTRACT.md) - model responsibilities, boundaries, and reproducibility
16. [PROMPT_SPEC.md](./PROMPT_SPEC.md) - fixed prompts and validation behavior
17. [WORKFLOW_SPEC.md](./WORKFLOW_SPEC.md) - end-to-end pipeline stages and failure behavior
18. [DATA_MODEL.md](./DATA_MODEL.md) - entities, storage boundaries, and retention
19. [OUTPUT_SCHEMA.md](./OUTPUT_SCHEMA.md) - backend/frontend result contract
20. [API_CONTRACT.md](./API_CONTRACT.md) - backend endpoints, payloads, and typed errors
21. [UI_SPEC.md](./UI_SPEC.md) - screens, states, and interaction model
22. [DEMO_FIXTURE_SPEC.md](./DEMO_FIXTURE_SPEC.md) - synthetic contract and expected findings
23. [TEST_AND_ACCEPTANCE_PLAN.md](./TEST_AND_ACCEPTANCE_PLAN.md) - validation and release evidence
24. [TRACEABILITY_MATRIX.md](./TRACEABILITY_MATRIX.md) - requirements-to-specification mapping
25. [RISK_REGISTER.md](./RISK_REGISTER.md) - delivery, security, model, and licensing risks
26. [IMPLEMENTATION_PHASE_PLAN.md](./IMPLEMENTATION_PHASE_PLAN.md) - incremental implementation phases and phase-completion enforcement
27. [IMPLEMENTATION_BACKLOG.md](./IMPLEMENTATION_BACKLOG.md) - sequenced build tasks and phase completion status
28. [EXECUTION_PLAN_48H.md](./EXECUTION_PLAN_48H.md) - two-day sequence and scope cuts
29. [DEMO_RUNBOOK.md](./DEMO_RUNBOOK.md) - repeatable presentation and fallback path
30. [PRE_IMPLEMENTATION_SELF_REVIEW.md](./PRE_IMPLEMENTATION_SELF_REVIEW.md) - superseded earlier self-review
31. [INDEPENDENT_AUDIT.md](./INDEPENDENT_AUDIT.md) - retained Claude review findings and conditional verdict
32. [RE_AUDIT.md](./RE_AUDIT.md) - Claude post-correction audit and readiness verdict
33. [RECONCILIATION_AUDIT.md](./RECONCILIATION_AUDIT.md) - current cross-document audit and correction resolutions
34. [REVIEW_GATE.md](./REVIEW_GATE.md) - mandatory stakeholder checkpoint before implementation
35. [CHANGE_CONTROL.md](./CHANGE_CONTROL.md) - enforcement for keeping docs updated

## Current State
- P0 Foundation and Fixed Result Demo, P1 Real Document Parsing, P2 Deterministic Playbook
  Engine, P3 Model-Assisted Clause Intelligence, P4 Retrieval and Guidance, P5 Admin and
  Provider Configuration, P6 Security and Evidence Hardening, and P7 Hosted Demo and Polish
  are implemented and verified, including a live Docker Ollama + `qwen3:4b` golden-fixture
  verification (P3, 4/4 runs identical, one egress-blocked), a live Qdrant-backed retrieval
  verification (P4, retrieval-on vs retrieval-off produced identical rule outcomes), a live
  admin-config save/reject/test-connection verification (P5, driven in the real browser and
  via `curl` against the running Docker stack), a live security-control verification (P6:
  SSRF blocklist, upload-size early rejection, log redaction, lazy review-record retention,
  optional Qdrant API-key auth including a real empty-string-key bug found and fixed, CORS,
  and an egress-blocked default-path run), and a hosted-demo packaging verification (P7:
  demo access Basic Auth, backend-locked config, same-origin frontend/backend serving, all
  verified against the built hosted Docker image run locally; see `IMPLEMENTATION_PHASE_PLAN.md`
  P0-P7 Completion/Live Verification Notes and `docs/SECURITY_EVIDENCE.md` for the factual
  command/result evidence). The deterministic P2 path remains the default for clause
  extraction and retrieval; no real hosted model provider was implemented, and the hosted
  demo is deterministic-only by design (D-05 remains deliberately open).
- **P7 is complete and accepted.** D-07 is accepted (Render, `render.yaml`/
  `backend/Dockerfile.hosted` packaging). Actually running that config against a live Render
  account to obtain a real public URL is **explicitly deferred to a later
  polish/optimization phase, by decision — not a P7 exit-criteria gap.**
  `docs/DEMO_RUNBOOK.md`'s hosted-URL and generated-fixture-artifact fields stay `TBD` until
  that later phase.
- The pre-implementation specification pack is `PASS WITH CONDITIONS`.
- The full reconciliation and independent-review corrections are recorded in `RECONCILIATION_AUDIT.md`; the original independent report is retained in `INDEPENDENT_AUDIT.md`, and the post-correction audit is retained in `RE_AUDIT.md`.
- Implementation may continue for local pipeline work; a real hosted model provider (D-05)
  remains a separate, not-yet-forced decision.
- Phase status is tracked in `IMPLEMENTATION_PHASE_PLAN.md`; P0-P7 are `complete`. The live
  public URL is tracked there as deferred work for a later phase, not as open P7 scope.
- **Schema-change reminder:** P4 added a new `Finding.guidance_json` column. There is no
  migration tooling in this prototype — a SQLite volume created before P4 needs
  `docker compose down -v` before the updated backend will run against it. P5, P6, and P7
  made no schema changes.
- **Security evidence:** `docs/SECURITY_EVIDENCE.md` (P6, extended in P7) is a factual,
  command/result/date/limitation evidence log for the security controls added in P6 — SSRF
  hardening, upload-size defense-in-depth, log redaction, retention, Qdrant auth, CORS,
  egress-blocked verification, port inventory, temp-file cleanup — and in P7 — hosted-demo
  access control, config lock, and deployment shape (section 10).

## Rule of Use
- Before implementing anything, read the relevant spec files above.
- If any implementation changes, update the affected spec files in the same change set.
- If scope changes, update `PART2_REQUIREMENTS.md` first.
- At the end of every work session, update `AGENT_HANDOFF.md` and `PLAN.md`.
- At the end of every implementation phase, follow the enforcement checklist in `IMPLEMENTATION_PHASE_PLAN.md`.
- If an architecture decision changes, update `ARCHITECTURE_DECISIONS.md` before implementation.
- D-07 is accepted (Render, Docker Web Service packaging) and P7 hosted-demo packaging is
  complete. D-05 remains open — do not implement a real hosted model provider until D-05 is
  explicitly accepted. Going live on a public URL is deferred to a later polish/optimization
  phase; this is not a P7 blocker.

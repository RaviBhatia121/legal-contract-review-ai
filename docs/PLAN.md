# Part 2 Plan

## Goal
Build a working intranet portal prototype for the Legal department that follows the case study exactly:
- Strictly agentic and structured
- No chatbot interface
- Upload a document and return structured, annotated risk findings
- Use a local-first architecture that can be explained clearly in the demo

## Scope
In scope:
- Legal contract review workflow
- Clause extraction
- Risk classification
- Playbook deviation detection
- Approved-template drafting support for flagged legal risks
- Structured output presentation
- Hosted demo URL
- Admin/configuration view to show enterprise flexibility

Out of scope:
- Chatbot-style interaction
- HR or Procurement workflows
- Anything beyond the Legal use case for Part 2

## Pre-Implementation Status
- [x] Requirements and scope documentation: complete
- [x] Master index and specification pack: complete
- [x] Architecture decisions and component boundaries: complete
- [x] Security, test, traceability, and handoff rules: complete
- [x] Original case-study source validation: complete
- [x] Technology and license validation: complete
- [x] Model/pipeline contract and deterministic playbook: complete
- [x] Data model, synthetic fixture, backlog, and risk register: complete
- [x] Prompt, rule-evaluation, and 48-hour execution specifications: complete
- [x] Internal pre-implementation consistency review: complete
- [x] Full cross-document reconciliation audit: complete
- [x] Monorepo strategy and multilingual-ready MVP boundary: complete
- [x] Final pre-review green-signal audit: complete
- [x] Independent Claude audit reconciliation and required specification corrections: complete
- [x] Claude post-correction re-audit and low-severity fixture correction: complete
- [x] Specification review and decision approval: pass with conditions

## Implementation Status
- [x] Portal shell and navigation: complete (React/Vite, `/review/new`, `/reviews/:id`, `/admin/model`)
- [x] Document upload flow: complete (upload -> job -> parsed document -> rule-evaluated findings; P3 model path is implemented but awaits live Ollama verification)
- [x] Real document parsing: complete (P1 — pypdf/python-docx; page count, language, provenance from real parsed documents)
- [x] Clause extraction pipeline: complete (P2 — deterministic, fixture-oriented segmentation; not general contract parsing, see `IMPLEMENTATION_PHASE_PLAN.md` P2 notes)
- [x] Risk classification logic: complete (P2 — max-severity aggregation, no averaging)
- [x] Playbook deviation checks: complete (P2 — 27-rule deterministic engine, `playbooks/defense-services-v1.json`)
- [x] Structured result schema implementation: complete — real P2 findings now match `OUTPUT_SCHEMA.md`, not the P0 fixed result
- [x] Results UI with annotations: complete (findings list, filters, missing-clause distinction)
- [x] Admin/configuration screen: complete (P5 — editable form with provider select, model name, Ollama base URL, write-only credential, Save, and Test connection; only `ollama` saveable, others shown "Not enabled" and rejected server-side; `/config/test` real Ollama ping since P3)
- [x] Model-assisted clause intelligence: complete (P3 — provider-neutral adapter, Ollama adapter, lazy Haystack pipeline, schema-validated model output, real classification-based `DOCUMENT_NOT_APPLICABLE`); current browser-demo runtime uses shared on-prem Ollama VM (`qwen3.6:35b`) with rules-only fallback; historical live Docker Ollama verification passed (4/4 runs identical), see `IMPLEMENTATION_PHASE_PLAN.md` P3 Live Verification Notes
- [x] Supplemental retrieval and guidance: complete (P4 — Qdrant-backed guidance retrieval keyed by rule_id, real local embeddings via Docker Ollama `qllama/multilingual-e5-small`, 27-item authored guidance corpus, post-processing only — `rule_engine.py` untouched); live docker-compose diff confirmed retrieval-on/off produce identical rule outcomes, see `IMPLEMENTATION_PHASE_PLAN.md` P4 Completion Notes
- [x] Provider portability admin UI: complete (P5/P7 — Ollama is the only enabled adapter; hosted model mode uses the same Ollama adapter when Render reaches the configured endpoint), see `IMPLEMENTATION_PHASE_PLAN.md` P5/P7 Completion Notes
- [x] Security-conscious local deployment setup: complete (P6 — SSRF hardening, defense-in-depth upload size guard, log redaction, PoC retention enforcement, optional Qdrant API-key auth, CORS/egress evidence; factual record in `docs/SECURITY_EVIDENCE.md`)
- [x] Hosted demo packaging: complete (P7 — `backend/Dockerfile.hosted`, `render.yaml`, demo
  access auth, backend-locked config, same-origin serving, Ollama model-mode env support;
  built and verified locally, see `docs/SECURITY_EVIDENCE.md` §10)
- [ ] Hosted demo live URL: **deferred to a later polish/optimization phase, by explicit
  decision — not a P7 blocker.** Packaging is complete and accepted as-is; only the actual
  Render deploy action and its downstream evidence (screenshots, filled-in runbook `TBD`
  fields) are deferred; see `docs/DEMO_RUNBOOK.md` and `IMPLEMENTATION_PHASE_PLAN.md` P7
  Completion Notes.
- [x] Validation against case study requirements: complete except the deferred live public URL.
  The local repository/prototype covers the Legal upload-to-structured-risk workflow,
  local/open-source model path, Qdrant/vector role, Haystack orchestration, frontend portal,
  secure data-flow walkthrough, and approved-template drafting support. The remaining
  Render deploy action and live URL evidence are tracked in `DEMO_RUNBOOK.md`.
- [x] P8 UI/UX and demo polish: complete — P8.1 Dashboard API complete (`GET /api/v1/reviews`,
  retention-aware, summary-only, aggregate counts, 9 new tests, 158 backend tests total); P8.2
  Brand and Shell complete (navy/gold palette, new favicon, unused `icons.svg` deleted,
  `:focus-visible`, header/footer/mobile polish); P8.3 Dashboard/Home complete (`/` now
  renders real review-history metrics and a recent-reviews table from
  `GET /api/v1/reviews?limit=50`; `Dashboard` added as the first nav item, visible in both
  local and demo mode; no fake ROI/value metrics; 7 new frontend tests, 17/17 total); P8.4
  Upload Screen Polish complete (`/review/new` now has a playbook summary card, 5-stage
  workflow strip, and a hosting-neutral trust note that avoids "on-premises"/"on-prem"/
  "air-gapped" wording; upload mechanics unchanged; 5 new frontend tests, 22/22 total; 158/158
  backend unaffected); P8.5 Findings Screen Polish complete (`/reviews/:reviewId` now shows a
  compliance banner, severity-grouped findings, a separate missing-clauses section, and
  field-labeled evidence/reasoning/recommendation, with all fields, filters, and polling
  behavior preserved; 4 new frontend tests, 26/26 total; 158/158 backend unaffected); P8.6
  Admin Screen Polish complete (`/admin/model` now has runtime-provider posture cards,
  current-config summary, provider catalog cards, security notes, and connection-test panel;
  cloud providers remain disabled placeholders, D-05 accepted for Ollama-only hosted model execution, credentials remain
  write-only; 28/28 frontend tests); P8.7 final validation complete (backend 158/158,
  frontend 28/28, frontend build clean, Docker backend/frontend healthy, live fixture upload
  completed with `overall_risk: Critical`, 7 findings, and 1 missing clause); P8.8 Admin
  Playbook Viewer complete (`/admin/playbook` plus `GET /api/v1/playbooks/active`, read-only
  active playbook/rule catalogue, no CRUD or risk-behavior change; backend 163/163, frontend
  33/33, frontend build clean)

## Phase Status
See `IMPLEMENTATION_PHASE_PLAN.md` for phase-level delivery contracts and end-of-phase documentation enforcement.
- P0 Foundation and Fixed Result Demo: complete
- P1 Real Document Parsing: complete
- P2 Deterministic Playbook Engine: complete
- P3 Model-Assisted Clause Intelligence: complete (4/4 live Docker Ollama `qwen3:4b` runs identical, including 1 egress-blocked)
- P4 Retrieval and Guidance: complete (live retrieval-on/off comparison confirmed identical rule outcomes)
- P5 Admin and Provider Configuration: complete (provider portability via UI/catalog/interface only; no proprietary/cloud adapter; D-05 accepted for Ollama-only hosted model execution)
- P6 Security and Evidence Hardening: complete (SSRF/redaction/retention/Qdrant-auth/CORS/egress-blocked evidence; see `docs/SECURITY_EVIDENCE.md`)
- P7 Hosted Demo and Polish: complete — the live public URL is deferred to a later polish/optimization phase by explicit decision, not treated as open P7 scope; see `docs/IMPLEMENTATION_PHASE_PLAN.md` P7 Completion Notes and `docs/DEMO_RUNBOOK.md`
- P8 UI/UX and Demo Polish: complete — see `docs/P8_UI_UX_POLISH_PLAN.md` and `docs/IMPLEMENTATION_PHASE_PLAN.md` P8.1-P8.8 Completion Notes; hosting/live URL and PDF/export remain out of scope
- P9 Case-Study Alignment: complete — `/architecture` explains the local stack and secure
  data flow; findings include approved-template draft clause language; dashboard/review
  screens explicitly show Qdrant supplemental-guidance status; no risk-decision behavior
  changed; backend 164/164, frontend 38/38, frontend build clean, Docker rebuild and live
  upload smoke test passed

## Working Definition
The prototype should:
1. Accept a legal document upload.
2. Process the document through a deterministic pipeline.
3. Return a structured list of clauses, risks, and deviations.
4. Provide approved-template drafting support for flagged risks, with legal approval required.
5. Display the output in a clear intranet-style portal.
6. Demonstrate the local stack, secure data flow, model path, and vector database role.

## Update Rule
This file should be updated as implementation progresses.
- Keep status labels consistent.
- Only mark a step complete when the code or artifact is actually working.
- Do not expand scope beyond Part 2 requirements.
- Implementation may start because `REVIEW_GATE.md` is `PASS WITH CONDITIONS`.
- Resolve hosted provider and hosting platform before hosted integration and deployment packaging.
- At the end of each phase, follow `IMPLEMENTATION_PHASE_PLAN.md` and update every affected document before moving to the next phase.

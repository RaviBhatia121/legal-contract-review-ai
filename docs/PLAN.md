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
- Structured output presentation
- Hosted demo URL
- Admin/configuration view to show enterprise flexibility

Out of scope:
- Chatbot-style interaction
- Human-in-the-loop drafting features
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
- [x] Model-assisted clause intelligence: complete (P3 — provider-neutral adapter, Docker Ollama adapter with `qwen3:4b`, lazy Haystack pipeline, schema-validated model output, real classification-based `DOCUMENT_NOT_APPLICABLE`); live Docker Ollama verification passed (4/4 runs identical), see `IMPLEMENTATION_PHASE_PLAN.md` P3 Live Verification Notes
- [x] Supplemental retrieval and guidance: complete (P4 — Qdrant-backed guidance retrieval keyed by rule_id, real local embeddings via Docker Ollama `qllama/multilingual-e5-small`, 27-item authored guidance corpus, post-processing only — `rule_engine.py` untouched); live docker-compose diff confirmed retrieval-on/off produce identical rule outcomes, see `IMPLEMENTATION_PHASE_PLAN.md` P4 Completion Notes
- [x] Provider portability admin UI: complete (P5 — no real hosted adapter; D-05 remains open), see `IMPLEMENTATION_PHASE_PLAN.md` P5 Completion Notes
- [x] Security-conscious local deployment setup: complete (P6 — SSRF hardening, defense-in-depth upload size guard, log redaction, PoC retention enforcement, optional Qdrant API-key auth, CORS/egress evidence; factual record in `docs/SECURITY_EVIDENCE.md`)
- [x] Hosted demo packaging: complete (P7 — `backend/Dockerfile.hosted`, `render.yaml`, demo
  access auth, backend-locked config, same-origin serving, demo banner with case-study
  narrative disclaimer; built and verified locally, see `docs/SECURITY_EVIDENCE.md` §10)
- [ ] Hosted demo live URL: **deferred to a later polish/optimization phase, by explicit
  decision — not a P7 blocker.** Packaging is complete and accepted as-is; only the actual
  Render deploy action and its downstream evidence (screenshots, filled-in runbook `TBD`
  fields) are deferred; see `docs/DEMO_RUNBOOK.md` and `IMPLEMENTATION_PHASE_PLAN.md` P7
  Completion Notes.
- [ ] Validation against case study requirements: pending (P3/P4/P5/P6/P7 are all
  live-verified against their own local/built-image evidence; full end-to-end validation
  against a live public URL is part of the deferred later polish phase, not P7)

## Phase Status
See `IMPLEMENTATION_PHASE_PLAN.md` for phase-level delivery contracts and end-of-phase documentation enforcement.
- P0 Foundation and Fixed Result Demo: complete
- P1 Real Document Parsing: complete
- P2 Deterministic Playbook Engine: complete
- P3 Model-Assisted Clause Intelligence: complete (4/4 live Docker Ollama `qwen3:4b` runs identical, including 1 egress-blocked)
- P4 Retrieval and Guidance: complete (live retrieval-on/off comparison confirmed identical rule outcomes)
- P5 Admin and Provider Configuration: complete (provider portability via UI/catalog/interface only; no real cloud adapter, D-05 remains open)
- P6 Security and Evidence Hardening: complete (SSRF/redaction/retention/Qdrant-auth/CORS/egress-blocked evidence; see `docs/SECURITY_EVIDENCE.md`)
- P7 Hosted Demo and Polish: complete — the live public URL is deferred to a later polish/optimization phase by explicit decision, not treated as open P7 scope; see `docs/IMPLEMENTATION_PHASE_PLAN.md` P7 Completion Notes and `docs/DEMO_RUNBOOK.md`

## Working Definition
The prototype should:
1. Accept a legal document upload.
2. Process the document through a deterministic pipeline.
3. Return a structured list of clauses, risks, and deviations.
4. Display the output in a clear intranet-style portal.
5. Demonstrate that the system can be configured for enterprise deployment.

## Update Rule
This file should be updated as implementation progresses.
- Keep status labels consistent.
- Only mark a step complete when the code or artifact is actually working.
- Do not expand scope beyond Part 2 requirements.
- Implementation may start because `REVIEW_GATE.md` is `PASS WITH CONDITIONS`.
- Resolve hosted provider and hosting platform before hosted integration and deployment packaging.
- At the end of each phase, follow `IMPLEMENTATION_PHASE_PLAN.md` and update every affected document before moving to the next phase.

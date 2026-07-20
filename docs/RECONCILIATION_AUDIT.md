# Part 2 Cross-Document Reconciliation Audit

## Audit Date and Outcome
- Date: 2026-07-18
- Scope: every Markdown document in `Part2/`
- Authority used: original case-study PDF -> `CASE_STUDY_BASELINE.md` -> `PART2_REQUIREMENTS.md` -> accepted architecture decisions -> detailed specifications
- Outcome: `RECONCILED - REVIEW GATE PASSED WITH CONDITIONS`
- Implementation authorization: granted for scaffold and local pipeline work; hosted integration/deployment remain gated by D-05 and D-07

## Reconciled Baseline
- Product: Legal Contract Risk Review intranet portal, not a chatbot.
- Workflow: upload -> validate -> local parse -> applicability check -> clause classify -> load all applicable rules and retrieve supplemental guidance -> extract normalized attributes -> deterministic rule evaluation -> validate -> persist -> render.
- Decision authority: application rules own findings, severity, explanations, actions, and overall risk.
- AI role: bounded clause classification and attribute extraction through schema-validated prompts.
- Vector role: Qdrant ranks supplemental guidance/examples and can never exclude an applicable rule.
- Hosted mode: access-restricted Demo mode, synthetic contracts only, optional selected cloud provider.
- Enterprise target: fully local stack with Ollama-compatible inference and runtime egress denied.
- Planning stack: React/Vite, FastAPI, Haystack, Docling, Qdrant, SQLite, Docker Ollama/Qwen, and multilingual E5 embeddings.

## Conflicts Found and Corrected

| ID | Conflict | Reconciliation |
|---|---|---|
| RC-01 | Architecture placed Qdrant retrieval before model clause classification | Corrected sequence to classify first, then load rules/retrieve guidance, then extract attributes |
| RC-02 | Qdrant was described as optional, candidate-rule filtering, and an accepted role in different files | Standardized it as a proposed supplemental-guidance role that never filters applicable rules |
| RC-03 | Required clause types lacked explicit missing-clause rule IDs | Added and mapped missing rules for all eight required clause types |
| RC-04 | Demo fixture wording could trigger rules different from its expected results | Defined exact clause conditions and eight exact expected rule IDs/counts |
| RC-05 | Output example summary counts did not equal the returned arrays | Corrected example counts and clarified that totals include both finding arrays |
| RC-06 | Output provenance used prompt version `1.0.0` while prompt spec used `1.0-draft` | Standardized on `1.0-draft` |
| RC-07 | Low-confidence output required a rule ID but no rule existed | Added `REV-001` and aligned confidence, presence, and needs-review behavior |
| RC-08 | Model-assisted explanation drafting conflicted with deterministic application-owned actions | Removed explanation drafting from model tasks; rule templates now own explanation and action text |
| RC-09 | Finding types were not deterministically derived from rules | Added explicit missing, compliant, needs-review, and deviation mappings |
| RC-10 | API/UI processing stages did not share a precise status contract | Added an in-progress schema and a closed `current_stage` enumeration mapped to broad API statuses |
| RC-11 | Data model omitted fields required by output/error/provenance contracts | Added nullable clause references, confidence, needs-review, safe failure fields, deployment, retrieval, and page metadata |
| RC-12 | Hosted access was optional in architecture wording and demo data allowed public contracts in one file | Made hosted access restriction required and standardized hosted input to synthetic contracts only |
| RC-13 | UI listed four selectable providers while backlog permitted one hosted adapter | Defined a provider catalog with only implemented/allowlisted adapters selectable; PoC requires Ollama plus one hosted adapter |
| RC-14 | Fixture generation was scheduled after the parser was supposed to use it | Moved fixture and expected-JSON generation before parsing in backlog and 48-hour plan |
| RC-15 | Deployment gating referenced the pre-implementation specification gate instead of executed tests | Deployment now requires applicable security checks in `TEST_AND_ACCEPTANCE_PLAN.md` to pass |
| RC-16 | Earlier self-review claimed no conflicts before this deeper audit | Marked the earlier review superseded and made this file the current audit record |
| RC-17 | Admin API accepted provider credentials without defining secure storage behavior | Defined environment bootstrap plus a write-only in-memory Demo override; prohibited plaintext database persistence |
| RC-18 | Hosted cloud execution could be mistaken for proof that the required local open-source model was utilized | Kept the disclosed synthetic cloud demo, but made a successful egress-blocked Ollama/Qwen golden-fixture run mandatory final evidence |
| RC-19 | Empty, non-contract, and out-of-scope document behavior was undefined | Added an applicability stage, typed failures, no-fabricated-findings rule, fixtures, backlog work, and acceptance tests |
| RC-20 | Status and display-stage mapping was derivable but not explicit | Added the closed status-to-`current_stage` mapping, including `checking_applicability` |
| RC-21 | Low-confidence evidence could optionally produce both review and missing findings | Made dual emission deterministic when no accepted candidate establishes required-clause presence and added a boundary test |
| RC-22 | Runtime config and playbook/version metadata drifted across contracts | Added `synthetic_data_only`, canonical `playbook_id`, and standardized draft component versions |
| RC-23 | Hosted performance target lacked a reference environment | Marked it provisional until host/model details and observed duration are recorded |

## Structural Checks Passed
- Every relative Markdown link resolves to an existing file.
- Every Part 2 document except the index itself appears in the master index, and every document appears in the change-control set.
- Playbook and rule-evaluation specifications contain the same 27 unique rule IDs.
- The fixture's eight expected rule IDs all exist in both rule sources.
- API status values match the data model, output schema, workflow, and UI.
- File type, 15 MB size, 100-page limit, retention, and deployment-mode rules are consistent.
- All implementation tasks remain pending.
- No stale synchronous review endpoints or earlier schema field names remain.

## Open Items That Are Not Conflicts
The following are deliberately unresolved and centralized in `OPEN_DECISIONS.md`:
- final acceptance of React/Vite and SQLite
- final acceptance of Docker Ollama/Qwen and multilingual E5 reference models
- Qdrant supplemental-guidance role
- hosted authentication mechanism
- hosted model provider
- hosting platform
- compliant-finding display default
- hosted-demo credential lifecycle

These choices must be accepted or replaced during stakeholder review. Any replacement requires the synchronized updates defined in `CHANGE_CONTROL.md`.

## Auditor Recommendation
Proceed to the stakeholder specification review using `OPEN_DECISIONS.md` and `REVIEW_GATE.md`. Do not begin implementation until the gate records `PASS` or `PASS WITH CONDITIONS`.

## Post-Audit Additions
After the reconciliation completed, three previously implicit boundaries were documented without changing the reconciled workflow:
- `ADR-007` accepts a monorepo rooted at `Part2/`, with its layout and dependency rules in `REPOSITORY_STRATEGY.md`.
- `ADR-008` keeps the English golden fixture as the MVP gate while requiring Unicode-safe, Indonesian-ready design and avoiding an unvalidated multilingual production claim.
- Proposed decision `D-12` defines the PoC job runner and restart behavior; it requires stakeholder acceptance before backend scaffolding.
- A final semantic audit replaced the English-only BGE embedding proposal with MIT-licensed `intfloat/multilingual-e5-small`, aligning retrieval with the Indonesian-ready architecture.
- Post-P3 model decision update: D-03 now uses Docker-based Ollama with Apache-2.0
  `qwen3:4b` as the lightweight PoC validation model. Qwen2.5-7B-Instruct remains an
  optional stronger local validation candidate if the lightweight model fails the golden
  fixture. Qwen2.5-3B-Instruct and Llama 3.2 3B are not the baseline because their licenses
  do not match the preferred permissive-license rule for this case study.

The structural validation checks were rerun after these additions.

## Final Pre-Review Green-Signal Audit
- Date: 2026-07-18
- Result: `GREEN - READY FOR STAKEHOLDER REVIEW`
- Discrepancy found: the proposed English-only embedding model conflicted with the Indonesian-ready architecture.
- Fix applied: replaced it everywhere with MIT-licensed `intfloat/multilingual-e5-small`; Indonesian retrieval quality remains subject to smoke testing and is not presented as production-validated.
- Final checks: master-index parity passed, change-control parity passed, all relative links resolved, all seven JSON examples parsed, the 27-rule playbook/predicate sets matched, all eight fixture rules resolved, stale terminology scan passed, and all implementation items remained pending.

## Independent Review Reconciliation
- Reviewer artifact: `INDEPENDENT_AUDIT.md`
- Verdict received: `READY WITH REQUIRED CORRECTIONS` / `PASS WITH CONDITIONS`
- Resolution: all High, Medium, and metadata corrections were incorporated except the suggestion to require Ollama on the publicly hosted instance. That suggestion was intentionally resolved through mandatory egress-blocked local evidence because the agreed hosted Demo mode may use a cloud provider with synthetic data. As of the post-P3 model decision update, that local evidence path is Docker Ollama + `qwen3:4b`.
- Remaining gate work: stakeholder acceptance of proposed/open decisions in `OPEN_DECISIONS.md`; no implementation work has started.

## Post-Correction Re-Audit
- Reviewer artifact: `RE_AUDIT.md`
- Verdict received: `READY FOR REVIEW APPROVAL` / `PASS WITH CONDITIONS`
- Resolution: the only actionable document looseness was the golden-fixture confidence band. `DEMO_FIXTURE_SPEC.md` and `TEST_AND_ACCEPTANCE_PLAN.md` now require expected clause classifications to be `>= 0.80`, and the golden fixture explicitly asserts zero `needs_review` findings.
- Remaining gate work: stakeholder acceptance or replacement of proposed/open decisions in `OPEN_DECISIONS.md`; no implementation work has started.

## Review Gate Approval
- Reviewer: Ravi Bhatia
- Date: 2026-07-18
- Result: `PASS WITH CONDITIONS`
- Accepted decisions: D-01 React/Vite, D-02 SQLite, D-03 Docker Ollama with `qwen3:4b` for PoC local-model validation, D-04 multilingual E5, D-06 restricted hosted auth, D-09 Qdrant supplemental-guidance role, D-10 collapsed compliant findings, D-11 demo credential lifecycle, and D-12 in-process PoC job runner.
- Remaining open decisions: D-05 hosted model provider and D-07 hosting platform.
- Implementation status: P0 scaffold may start; hosted integration and deployment packaging must wait for D-05 and D-07.

## Phase Plan Reconciliation
- Reviewer artifact: Claude targeted phase-plan audit
- Verdict received: `READY WITH MINOR FIXES`
- Resolution: `IMPLEMENTATION_BACKLOG.md` was re-bucketed to match `IMPLEMENTATION_PHASE_PLAN.md` exactly across P0-P7. The duplicate P1 heading was removed, Docling parsing moved to P1, deterministic rule work moved to P2, Haystack/model work moved to P3, Qdrant retrieval moved to P4, admin/provider configuration moved to P5, security evidence moved to P6, and hosted deployment/polish moved to P7.
- Implementation status: all backlog items remain unchecked; P0 may start.
- Follow-up: `AGENT_HANDOFF.md` was corrected so the P0 next task no longer includes real text parsing.

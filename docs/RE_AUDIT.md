# Part 2 Re-Audit (Post-Correction)

> Historical note: this re-audit is retained as a point-in-time review. The current model
> decision was superseded by the post-P3 update: Docker Ollama with `qwen3:4b` is now the
> lightweight PoC validation path; see `RECONCILIATION_AUDIT.md`.

## Verdict
**READY FOR REVIEW APPROVAL** — high confidence.

The correction pass genuinely worked. All 3 High, all 5 Medium, and all 5 Low prior findings are resolved with consistent, coordinated edits across the documents that needed to move together (not one-doc partial fixes). The golden fixture is now fully self-consistent with the rule predicates (all 8 expected findings traced through the predicate logic and each fires exactly as asserted). The pack is legitimately ready to enter the stakeholder review gate. The only items outstanding are (a) one minor latent looseness the correction pass itself introduced (fixture confidence band vs. the needs_review threshold — Low) and (b) the deliberate, by-design "Proposed" status of the three scaffold-blocking decisions, which the REVIEW_GATE exists to resolve. Neither blocks review approval.

## Correction Status

**A-H1 (hosted demo may run cloud LLM) — RESOLVED.** The pack chose the prior audit's permitted OR-branch (required local-run artifact rather than forcing Ollama live on the hosted URL), and applied it consistently across every document that needed it: `ARCHITECTURE.md:61` (Scope Guardrails: "Final requirement evidence includes a successful egress-blocked Ollama/Qwen run; cloud execution cannot substitute for it"), `CASE_STUDY_BASELINE.md:30` (Known Interpretation Risk now mandates the egress-blocked local golden-fixture run), `OPEN_DECISIONS.md:14` (D-08 now **Accepted**), `EXECUTION_PLAN_48H.md:43`, `REVIEW_GATE.md:12,43`, plus reinforcement in `PART2_REQUIREMENTS.md:53`, `TEST_AND_ACCEPTANCE_PLAN.md:66`, `TRACEABILITY_MATRIX.md:20`. D-05 (which cloud provider) remaining "Open" is legitimate — provider selection is genuinely deferrable and does not undermine the fix.

**A-H2 (deterministic acceptance depended on unproven repeatability; P0 returned a hardcoded fixture) — RESOLVED.** `TEST_AND_ACCEPTANCE_PLAN.md:42-49` now requires a 3-run pinned-local-model repeatability test, with "at least one run must use the live Ollama/Qwen path with runtime egress blocked; a fixed fixture result cannot satisfy this criterion" (line 43) and "Record confidence values and result variance for all three runs" (line 46). Fixture confidence tuning is specified in `DEMO_FIXTURE_SPEC.md:35` and `TEST_AND_ACCEPTANCE_PLAN.md:47`. `DEMO_RUNBOOK.md:14-15` adds the local-verification and 3-run variance record fields; `DEMO_RUNBOOK.md:31` bars the fixed result from acceptance. Backlog `IMPLEMENTATION_BACKLOG.md:40` captures it. P0 still returns a fixed result (`IMPLEMENTATION_BACKLOG.md:13`) but it is now explicitly excluded from live-model acceptance evidence (`REVIEW_GATE.md:43`) — correct separation.

**A-H3 (no defined behavior for non-contract / zero-clause document) — RESOLVED.** A typed applicability stage now exists end-to-end: `WORKFLOW_SPEC.md:28-35` (Stage 3 emits `NO_REVIEWABLE_TEXT` / `DOCUMENT_NOT_APPLICABLE` and "Do not fabricate missing-clause findings when applicability has not been established"), `API_CONTRACT.md:115-116` (both new error codes), `OUTPUT_SCHEMA.md:133` (validation rule barring fabricated missing-clause findings on those outcomes), `DEFENSE_PLAYBOOK_TEMPLATE.md:82-85` (evaluation-order step 1), `RULE_EVALUATION_SPEC.md:51`, `TEST_AND_ACCEPTANCE_PLAN.md:11-12`, and dedicated fixtures in `DEMO_FIXTURE_SPEC.md:45-46`. Fully coordinated.

**A-M1 (48h plan leans on cloud fallback under time pressure) — RESOLVED.** `EXECUTION_PLAN_48H.md:42` orders the response as "first simplify the bounded prompt, tune only the synthetic fixture wording... test a smaller supported quantization or alternate local commercially usable model" before anything else; line 43 states cloud "cannot replace the mandatory successful local-model verification. If no local model passes, record the case-study requirement as unmet rather than claiming completion." Scope-cut item 2 keeps "the selected demo provider plus Ollama."

**A-M2 (120s/20-page target unsubstantiated) — RESOLVED.** `NON_FUNCTIONAL_REQUIREMENTS.md:11` now reads "Provisional objective... This is not an acceptance gate until measured; the evidence must record host CPU, memory, accelerator if any, provider/model, and observed duration."

**A-M3 (no explicit status↔current_stage mapping) — RESOLVED.** `OUTPUT_SCHEMA.md:119-128` adds an explicit "Status-to-stage mapping" table (queued→queued; parsing→parsing_document; analyzing→{checking_applicability, classifying_clauses, checking_playbook, extracting_attributes, evaluating_rules}; validating→validating_result; completed/failed→null).

**A-M4 (low-confidence clause: one or two findings ambiguity) — RESOLVED.** Definitive rule now stated identically in `DEFENSE_PLAYBOOK_TEMPLATE.md:104` and `RULE_EVALUATION_SPEC.md:55` ("For every relevant candidate below 0.60, emit REV-001. After all candidates are evaluated, emit the mapped missing-clause rule as well when no candidate at or above 0.60 establishes the required clause type. This behavior is mandatory, not optional, and both findings contribute to summary counts."). Unit/boundary test added at `TEST_AND_ACCEPTANCE_PLAN.md:49`.

**A-L1 (synthetic_data_only missing from DATA_MODEL) — RESOLVED.** `DATA_MODEL.md:53` adds `synthetic_data_only` to RuntimeConfiguration, matching `API_CONTRACT.md:57`.

**A-L2 (playbook_id vs playbook_version unreconciled) — RESOLVED.** `DEFENSE_PLAYBOOK_TEMPLATE.md:4` now declares canonical "Playbook ID: `defense-services-v1`" alongside "Playbook version: `1.0-draft`" (line 5); `DATA_MODEL.md:52` records `playbook_id` as the "active canonical playbook identifier"; `API_CONTRACT.md` uses `defense-services-v1`. Distinct fields, now consistent.

**A-L3 (mixed version conventions) — RESOLVED.** All component versions standardized to `1.0-draft` (`OUTPUT_SCHEMA.md:70-72` pipeline/playbook/prompt). RC-06 in `RECONCILIATION_AUDIT.md:29` documents the change. Grep confirms the only remaining `1.0.0` strings are inside the two audit reports describing the old state — not in any live spec.

**A-L4 (AUD-001 dual-purpose undocumented) — RESOLVED.** Explicitly documented at `DEFENSE_PLAYBOOK_TEMPLATE.md:106` and `RULE_EVALUATION_SPEC.md:65` ("AUD-001 emits missing_clause when the audit clause is absent and deviation when a clause exists but grants no customer audit right").

**A-L5 (cosmetic file-count mismatch in original task prompt) — NOT APPLICABLE / nothing to fix.** The prior audit itself scoped this as external to the pack; no pack change was required and none was needed.

## New Issues Introduced

**N-1 (Low) — Fixture confidence band does not cover the needs_review threshold. `DEMO_FIXTURE_SPEC.md:35` / `TEST_AND_ACCEPTANCE_PLAN.md:47`.** The correction pass added the qualifier that expected clause classifications must stay "outside the `0.55-0.65` threshold-risk band." That band only protects the **0.60** REV-001/missing-clause boundary. But the confidence rule (`DEFENSE_PLAYBOOK_TEMPLATE.md:103`) sets `needs_review: true` for anything **0.60–0.79**. A fixture clause classified at, say, 0.70 satisfies the stated "outside 0.55–0.65" band yet would emit `needs_review: true` findings — which the fixture's expected clean outcome (all findings `needs_review: false` in `OUTPUT_SCHEMA.md:50,63`; no needs-review items in the `DEMO_FIXTURE_SPEC.md` expected summary) does not anticipate. This is new because the band language did not exist at the time of the prior audit. It is Low severity because the golden-fixture assertions (`TEST_AND_ACCEPTANCE_PLAN.md:51-56`) do not explicitly assert `needs_review_count == 0`, so it is a looseness rather than a hard contradiction. Fix: require fixture classifications at `>= 0.80` (or add an explicit `needs_review_count: 0` fixture assertion).

**N-2 (Informational, not a defect) — ADR status vs. OPEN_DECISIONS status tension.** `ARCHITECTURE_DECISIONS.md:6-9` marks ADR-001 "Accepted" and lists React/Vite as a component, while `OPEN_DECISIONS.md:7` keeps D-01 (frontend framework) "Proposed." ADR-001 hedges this correctly ("Vite recommended for review"), so it is not a true contradiction — the thin-app decision is accepted; the specific framework choice remains a gate item. Noted only so the reviewer is not surprised.

No other new contradictions were found. All 8 golden-fixture findings were re-traced against the `RULE_EVALUATION_SPEC.md` predicates (DATA-001 Critical; CONF-002/SUB-001/AUD-001/LIAB-001/SEC-002 High; IP-002/TERM-004 Low) and confirmed each fires exactly once with the asserted severity and that no unintended rule (e.g. DATA-002/003, SUB-002, LIAB-002, SEC-001/003) fires given the fixture conditions — internally consistent between `DEMO_FIXTURE_SPEC.md` and `TEST_AND_ACCEPTANCE_PLAN.md`.

## Verification Results

- **JSON validity:** All 7 fenced JSON blocks parse (0 invalid).
- **Link resolution:** All 32 MASTER_INDEX relative links resolve; all cross-file links resolve, including `../CASE STUDY - Head of Enterprise AI.pdf`.
- **Rule-ID matching:** `DEFENSE_PLAYBOOK_TEMPLATE.md` and `RULE_EVALUATION_SPEC.md` each define exactly **27** rule IDs; identical sets. Fixture's 8 expected IDs are all a valid subset.
- **Parity:** All 33 files present in `CHANGE_CONTROL.md` sync set (0 missing); all appear in `MASTER_INDEX.md`.
- **Scaffold-blocking decisions D-01/D-02/D-12:** **NOT Accepted** — `OPEN_DECISIONS.md:7,8,18` all still show "Proposed." This is by design: `REVIEW_GATE.md:30,55` and `CHANGE_CONTROL.md:77` require the reviewer to flip these at the gate, and the pack is explicitly pre-review. Not a regression — the expected outstanding gate action.
- **License claims:** Unchanged from the previously-confirmed set and internally consistent — Qwen2.5-7B-Instruct Apache-2.0, multilingual-e5-small MIT, Docling MIT, Haystack 2.x Apache-2.0, Qdrant Apache-2.0, Ollama MIT, FastAPI/Vite MIT, SQLite public domain, Docker Compose Apache-2.0.

## Remaining Required Corrections

1. **(Optional, Low) Close N-1:** Tighten `DEMO_FIXTURE_SPEC.md:35` to require fixture classification confidence `>= 0.80` (or add an explicit `needs_review_count: 0` assertion to the golden-fixture assertions in `TEST_AND_ACCEPTANCE_PLAN.md:51-56`), so the fixture's clean expected output cannot collide with the 0.60–0.79 `needs_review` band.
2. **(Gate action, not a doc defect) Accept D-01, D-02, D-12** in `OPEN_DECISIONS.md` during the stakeholder review before backend/frontend scaffolding, per `REVIEW_GATE.md` enforcement. Copy any accepted architecture decisions into `ARCHITECTURE_DECISIONS.md` as its Change Rule requires.

That is the entire remaining list — dramatically shorter than the prior 13 substantive findings, confirming the correction pass succeeded.

## Final Recommendation

**PASS WITH CONDITIONS** — and the conditions are light:

- Condition 1 (procedural, mandatory before implementation): the reviewer explicitly accepts or replaces D-01/D-02/D-12 (and the other proposed decisions) at the `REVIEW_GATE`, since the pack is intentionally gated and these three block scaffolding.
- Condition 2 (optional polish): resolve N-1 by pinning fixture confidences `>= 0.80` or asserting `needs_review_count: 0`.

All 14 prior findings are genuinely resolved with coordinated multi-document edits, mechanical checks (JSON, 27 rule-ID parity, links, change-control/index parity) all pass, and the correction pass introduced only one Low-severity latent looseness. This documentation pack is ready to go into stakeholder review.

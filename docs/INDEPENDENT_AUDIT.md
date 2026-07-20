# Part 2 Independent Audit

> Historical note: this audit is retained as a point-in-time review. The current model
> decision was superseded by the post-P3 update: Docker Ollama with `qwen3:4b` is now the
> lightweight PoC validation path; see `RECONCILIATION_AUDIT.md`.

## Verdict

**READY WITH REQUIRED CORRECTIONS**

Confidence: High.

This is an unusually disciplined pre-implementation pack. Independently (not trusting the pack's own `RECONCILIATION_AUDIT.md`), I confirmed the things that most often break in AI-generated spec sets are actually sound here: all 7 JSON examples parse, every relative link resolves, the playbook and rule-evaluation specs share exactly the same 27 rule IDs, the eight fixture rule IDs all exist in both rule sources, and the demo fixture's expected findings are genuinely consistent with the deterministic predicates (I traced each of the eight conditions through `RULE_EVALUATION_SPEC.md` by hand). The four material license claims I web-verified — Qwen2.5-7B-Instruct (Apache-2.0), multilingual-e5-small (MIT), Docling (MIT) — are all accurate, and unlike the earlier fabricated-statistic problem in this project, I found **no invented CVE, benchmark, star count, or license claim** in this pack.

It is not a clean pass, however. There are real, non-fabricated issues: one High case-study-fidelity risk that is disclosed but unresolved (whether the hosted demo actually runs the open-source local model), a genuinely missing failure behavior (non-contract / zero-clause / non-applicable documents), a few minor schema drifts, and an aggressive timeline whose documented fallback path can quietly undercut the central requirement. None of these are hard contradictions that block scaffolding the P0 slice, so the pack is not "NOT READY" — but they are corrections a reviewer should require, so it is not a rubber-stamp approval either.

## Findings

### High

**A-H1 — Hosted demo may not actually "utilize" the open-source local model (case-study fidelity)**
- Severity: High
- Refs: `ARCHITECTURE.md:34` ("Approved cloud model may be configured for speed"), `EXECUTION_PLAN_48H.md:42` (stop condition: "If local model quality fails the expected rule outcomes, use the hosted provider for Demo mode"), `CASE_STUDY_BASELINE.md:29-30` (the pack's own "Known Interpretation Risk"), `OPEN_DECISIONS.md:11` (D-05 hosted provider still Open).
- Conflicting docs: The case study requires the PoC to "**specify and utilize** open-source, commercially viable models capable of running locally," delivered as a "hosted **local** demo link." The pack builds a public "Hosted Demo mode" that may run a proprietary cloud LLM, with the local model relegated to a "verified path" that may only be demonstrated with egress-blocked evidence rather than in the live demo.
- Why it matters: This is the single biggest way the strongest deliverable could fail to convince the interviewer. If the demo the reviewer clicks runs Anthropic/OpenAI/Gemini, the candidate has arguably demonstrated a cloud contract-review tool, not the required locally-runnable open-source one. The riskiest, least-certain work (getting a 7B model to reliably produce the expected findings) is deferred to Day 2 hours 0-5 with a cloud escape hatch.
- Recommended correction: Make it a review-gate condition that the **live hosted demo runs Qwen2.5-7B via Ollama** (self-hosted alongside the app), with the cloud provider demoted to an optional, clearly-labelled speed comparison only. If cloud must be the live path for latency reasons, require a second, recorded, egress-blocked local-model run of the same fixture to be shown in the walkthrough, not merely referenced. Resolve D-05 accordingly before the model-integration backlog item.
- Blocks implementation: No (blocks demo credibility, not scaffolding). Should block gate PASS without an explicit decision.

**A-H2 — Deterministic acceptance depends on unproven local-model repeatability; P0 returns a hardcoded result**
- Severity: High
- Refs: `TEST_AND_ACCEPTANCE_PLAN.md:40-43` (run golden fixture 3× on pinned local model; rule IDs/severities must match), `IMPLEMENTATION_BACKLOG.md:13` ("Return a schema-valid **fixed** review result"), `DEMO_RUNBOOK.md:27-29` (fallback keeps "a known-good structured result fixture"), `EXECUTION_PLAN_48H.md:42`.
- Why it matters: The pack is careful and honest that model generation is probabilistic (`MODEL_AND_PIPELINE_CONTRACT.md:4`), but the acceptance gate still requires exact rule-ID/severity stability across three runs. Temperature-0 on Ollama/llama.cpp is not guaranteed bit-identical, and a single clause-classification flip (e.g., 0.61 vs 0.59 crossing the REV-001/`0.60` threshold) can change finding counts. Because P0 legitimately returns a *fixed* fixture result, there is a real risk the demo shows the canned fixture rather than a live model classification — which the docs themselves warn against but do not prevent.
- Recommended correction: Add an explicit acceptance criterion that the golden fixture must pass **from a live local-model run** (not the fixed P0 result) at least once, and record the three-run variance as evidence. Pre-commit to what happens if a confidence value lands in the 0.55–0.65 band for the fixture (tune the synthetic clause text to sit well clear of 0.60). Keep the "do not represent fixture mode as a live run" rule (`DEMO_RUNBOOK.md:29`) as a gating check.
- Blocks implementation: No. Blocks an honest "deterministic" claim at demo time.

**A-H3 — No defined behavior for a non-contract, empty, or non-applicable document**
- Severity: High
- Refs: `DEFENSE_PLAYBOOK_TEMPLATE.md:81` (Evaluation Order step 1: "Determine document type and applicability" — but no outcome is specified when applicability is false), `WORKFLOW_SPEC.md` (stages 3-6 assume clauses exist), `API_CONTRACT.md:109-122` (no error code for "not a reviewable contract" / "no clauses found").
- Why it matters: If a user uploads a valid PDF that is not a services agreement (or Docling returns zero clauses), the required-clause logic will mark all eight required clause types absent, emit eight missing-clause High/Critical findings, and report overall risk High/Critical for a document that is not even a contract. That is a demo-breaking false result with no guardrail. This is a genuine missing failure behavior an implementer would otherwise have to invent.
- Recommended correction: Define an explicit outcome — e.g., a `DOCUMENT_NOT_APPLICABLE` typed error (or a `needs_review`-style "no reviewable clauses detected" result) triggered when zero clauses classify above threshold or applicability is false — and add it to `API_CONTRACT.md`, `WORKFLOW_SPEC.md`, `OUTPUT_SCHEMA.md`, and the test plan.
- Blocks implementation: No for P0 (fixture path), but must be resolved before the demo is exposed to arbitrary uploads.

### Medium

**A-M1 — 48-hour plan is aggressive and leans heavily on scope-cuts and the cloud fallback**
- Severity: Medium
- Refs: `EXECUTION_PLAN_48H.md` (Day 2 hours 0-5 cover Haystack wiring + local adapter + prompts + validated extraction + rule engine + persistence), `RISK_REGISTER.md:5` (R-01), `PRE_IMPLEMENTATION_SELF_REVIEW.md:37` ("two-day build remains aggressive").
- Why it matters: The plan is internally coherent and the scope-cut order (`EXECUTION_PLAN_48H.md:29-37`) is sensible, but three of the hardest, least-predictable integrations (Haystack 2.x, Qdrant, and reliable structured JSON from a local 7B) are compressed into Day 2. Realistically, a builder will end Day 2 relying on at least one documented fallback. The candidate has 2 extra polish days, which makes this feasible — but only if the fallbacks in A-H1/A-H2 do not erode the core requirement.
- Recommended correction: Explicitly time-box the local-model integration and pre-decide that if it slips, the fix is "ship Qwen/Ollama with a smaller/simpler fixture" rather than "switch the live demo to cloud." No document change strictly required; add a note to `EXECUTION_PLAN_48H.md` stop conditions.
- Blocks implementation: No.

**A-M2 — Performance target (20 pages / 120 s) is unsubstantiated and hardware is unspecified**
- Severity: Medium
- Refs: `NON_FUNCTIONAL_REQUIREMENTS.md:11`, `DEMO_FIXTURE_SPEC.md:11` (8-12 page fixture), `OUTPUT_SCHEMA.md:23-24` (example shows 18 clauses reviewed).
- Why it matters: With per-clause attribute extraction (P-02) plus segmentation, an 18-clause contract implies ~19 sequential model calls. On a modest local GPU/CPU this can approach or exceed 120 s; on cloud it is trivial. The 120 s figure appears with no stated hardware baseline — exactly the kind of precise-but-unbacked number to treat cautiously. It is a target rather than a measured claim, so it is not a fabrication, but it is currently unverifiable.
- Recommended correction: Either qualify the target with an assumed hardware profile and the intended concurrency of model calls (batched vs sequential), or mark it provisional until measured. Note that the on-premises hardware sizing lives in Part 1, not here.
- Blocks implementation: No.

**A-M3 — No explicit status ↔ current_stage mapping**
- Severity: Medium
- Refs: `WORKFLOW_SPEC.md:73-77` (status transitions), `OUTPUT_SCHEMA.md:109-116` (7 allowed `current_stage` values), `UI_SPEC.md:22-24`.
- Why it matters: Four `current_stage` values (`classifying_clauses`, `checking_playbook`, `extracting_attributes`, `evaluating_rules`) all fall under the single persisted status `analyzing`, but no document tabulates which substage maps to which broad status. It is derivable, but two implementers could map it differently, producing inconsistent polling UIs.
- Recommended correction: Add a small mapping table (status → allowed current_stage values) to `OUTPUT_SCHEMA.md` or `WORKFLOW_SPEC.md`.
- Blocks implementation: No.

**A-M4 — Low-confidence path can emit both a needs_review (REV-001) and a missing-clause finding for the same clause**
- Severity: Medium
- Refs: `DEFENSE_PLAYBOOK_TEMPLATE.md:100` ("A missing-clause finding may therefore also be emitted for completeness"), `RULE_EVALUATION_SPEC.md:54` ("REV-001 is evaluated before presence and clause-type predicates"), `OUTPUT_SCHEMA.md:124` ("Summary counts must equal the returned findings").
- Why it matters: A clause that exists but classifies at <0.60 becomes `unknown`, fires REV-001 (needs_review), and — because presence is not established — can also fire the mapped missing-clause rule. That is a defensible double-count, but the "may" makes it non-deterministic and it is not exercised by the fixture, so behavior is genuinely ambiguous and could break the "counts equal findings" invariant if implemented inconsistently.
- Recommended correction: State definitively whether a single low-confidence clause emits one finding (needs_review only) or two (needs_review + missing), and add a unit test.
- Blocks implementation: No (fixture avoids the case), but should be pinned before P1 rule engine.

### Low

**A-L1 — `synthetic_data_only` field in the config API is not in the data model.** `API_CONTRACT.md:56` returns `synthetic_data_only`, but `DATA_MODEL.md:45-52` RuntimeConfiguration has no such field. Add it or remove it.

**A-L2 — Two playbook identifiers are unreconciled.** `API_CONTRACT.md:16,54` uses `playbook_id: "defense-services-v1"`; `DEFENSE_PLAYBOOK_TEMPLATE.md:4` and provenance (`OUTPUT_SCHEMA.md:73`) use `playbook_version: "1.0-draft"`. The playbook template never declares its canonical `playbook_id`. Add `playbook_id: defense-services-v1` to the playbook doc so the API default has a source of truth.

**A-L3 — Mixed version conventions.** `OUTPUT_SCHEMA.md:72` uses `pipeline_version: "1.0.0"` (semver) while playbook/prompt use `"1.0-draft"`. Not a contradiction, but inconsistent; pick one convention.

**A-L4 — AUD-001 is dual-purpose (missing + deviation).** `DEFENSE_PLAYBOOK_TEMPLATE.md:36,72` and `RULE_EVALUATION_SPEC.md:64` make AUD-001 the only required clause whose "absent" case reuses a deviation rule rather than a dedicated `*-003/004` ID. It is documented and internally consistent, but asymmetric with the other seven required clauses and easy to mis-implement. Consider a note or an `AUD-003` for symmetry.

**A-L5 — Task-prompt count discrepancy (cosmetic).** The task brief refers to "27 markdown files"; the folder actually contains 32 `.md` files (all correctly indexed). No action needed on the pack; flagged only so the count is not mistaken for a missing-file problem.

## Case-Study Traceability

| Explicit Part 2 requirement | Status | Support |
|---|---|---|
| Functional working Legal intranet portal | Covered (spec only; unbuilt) | `PART2_REQUIREMENTS.md`, `UI_SPEC.md` |
| Agentic, structured, non-chat workflow | Covered | `WORKFLOW_SPEC.md`, `ARCHITECTURE_DECISIONS.md` ADR-003 |
| Deterministic / pre-prompted AI actions | Partially covered | Deterministic rules well-specified (`RULE_EVALUATION_SPEC.md`); model-level repeatability unproven (A-H2) |
| Legal: upload → structured annotated risk points, no chat | Covered | `OUTPUT_SCHEMA.md`, `DEMO_FIXTURE_SPEC.md`, `UI_SPEC.md` |
| Open-source, commercially viable local models | Covered in spec; Partially at demo | Licenses verified (Qwen Apache-2.0, e5 MIT); live-demo model unresolved (A-H1) |
| Vector database | Covered | Qdrant (`ARCHITECTURE.md`, `TECH_STACK_AND_LICENSES.md`) |
| Backend orchestration framework | Covered | Haystack 2.x (with documented fallback if it blocks the slice) |
| Frontend portal | Covered | React/Vite (`UI_SPEC.md`) |
| Working prototype access: repo + hosted local demo link | Partially covered | Repo layout defined (`REPOSITORY_STRATEGY.md`); demo URL `TBD`; "hosted local" interpreted as public cloud demo (A-H1) |
| Brief secure-local-data-flow walkthrough | Covered | `ARCHITECTURE.md` trust boundaries, `SECURITY_AND_DATA.md` |

No requirement is Missing or Conflicting; the two Partials both trace back to A-H1/A-H2.

## Cross-Document Reconciliation

- Requirements ↔ architecture ↔ workflow: consistent. Workflow stages, `current_stage` enum, and status enum agree across `WORKFLOW_SPEC.md`, `OUTPUT_SCHEMA.md`, `DATA_MODEL.md`, `UI_SPEC.md` (one precision gap: A-M3).
- API ↔ schema ↔ data model: consistent except A-L1 (`synthetic_data_only`) and A-L2 (playbook_id vs playbook_version).
- UI ↔ output: consistent (collapse rules, default filters, provenance drawer all match `OUTPUT_SCHEMA.md`/`DEFENSE_PLAYBOOK_TEMPLATE.md`).
- Playbook ↔ predicates ↔ fixture ↔ tests: **verified consistent.** 27 rule IDs match exactly across `DEFENSE_PLAYBOOK_TEMPLATE.md` and `RULE_EVALUATION_SPEC.md`; the fixture's 8 expected IDs (`DATA-001`, `CONF-002`, `SUB-001`, `AUD-001`, `IP-002`, `LIAB-001`, `TERM-004`, `SEC-002`) all resolve; counts (1 Critical + 5 High + 2 Low = 8, one missing-clause) are self-consistent and match `TEST_AND_ACCEPTANCE_PLAN.md:45-50`. Residual ambiguity only in the untested low-confidence path (A-M4).
- Security ↔ deployment: consistent and thorough (SSRF, prompt-injection boundary, Qdrant private-bind/auth, secret handling, egress-denied local mode, retention). No contradictions.
- Backlog ↔ timeline ↔ status: consistent; all implementation items are `pending` in `PLAN.md`, `IMPLEMENTATION_BACKLOG.md`, and `MASTER_INDEX.md`. Fixture generation correctly precedes parsing (RC-14 fix confirmed in both backlog and 48h plan).

## Open-Decision Review

| ID | Decision | Assessment |
|---|---|---|
| D-01 React/Vite | Correctly open, but effectively baked into every spec. Non-blocking to review; **needed at scaffold**. Should be accepted at the gate. |
| D-02 SQLite | Same as D-01. Sound for a PoC. **Needed at backend scaffold.** |
| D-03 Qwen2.5-7B via Ollama | Correctly open; license verified Apache-2.0. Recommend accept. Non-blocking until model integration. |
| D-04 multilingual-e5-small | Correctly open; MIT verified and it explicitly benchmarks Indonesian retrieval. Recommend accept. |
| D-05 Hosted demo provider | Genuinely open — but its resolution is entangled with A-H1 and should be decided *together with* the "live demo must run the local model" condition. Non-blocking for scaffolding. |
| D-06 Hosted auth | Correctly open; non-blocking until deployment. |
| D-07 Hosting platform | Genuinely open; non-blocking for build, blocking for the hosted URL deliverable. |
| D-08 Cloud-demo exception | Marked Accepted. Reasonable, but it is the crux of A-H1 — reconfirm with an explicit "local model runs live" guardrail attached. |
| D-09 Qdrant role | Correctly open; well-bounded (never excludes rules). Recommend accept. |
| D-10 Compliant-finding collapse | Correctly open; trivial UI choice. Non-blocking. |
| D-11 Demo credential lifecycle | Correctly open; security design is sound (in-memory, write-only, clears on restart). |
| D-12 Prototype job runner | Correctly open; **needed at backend scaffold**, and correctly flagged as such. |

None are unnecessary for the PoC. None are insufficiently specified except D-05, whose specification should be widened to state the local-model demo guarantee. Blocking-for-scaffold set: **D-01, D-02, D-12** (the pack itself says so in the "When Needed" column, which is correct).

## Implementation Readiness

An implementation agent **could begin the P0 vertical slice today without inventing requirements** — the fixture, output schema, API contract, and repo layout are precise enough to scaffold and return a schema-valid fixed result. Before going beyond P0, the following must be resolved (not invented):

1. Accept D-01, D-02, D-12 (scaffold-blocking).
2. Resolve A-H3 (non-contract / zero-clause behavior) — currently unspecified; an agent would have to guess.
3. Pin A-M4 (low-confidence single-finding vs double-finding rule).
4. Decide A-H1 (does the live hosted demo run Qwen/Ollama or a cloud model) before the model-integration and hosted-deploy items.
5. Add the A-M3 status↔substage mapping to avoid divergent polling UIs.
6. Fix the schema drifts A-L1/A-L2 so backend types are unambiguous.

Everything else (prompts, predicates, evidence rules, security controls, retention) is specified to a build-ready level.

## Verification Results

- **Files / index:** 32 `.md` files present; all 31 non-index files appear in `MASTER_INDEX.md` and all 32 appear in the `CHANGE_CONTROL.md` sync set. No orphans, no missing files.
- **Links:** All relative Markdown links resolve, including `../CASE STUDY - Head of Enterprise AI.pdf`. Verified programmatically.
- **JSON:** All 7 JSON examples (4 in `API_CONTRACT.md`, 3 in `OUTPUT_SCHEMA.md`) parse without error. Verified programmatically.
- **Rule IDs:** `DEFENSE_PLAYBOOK_TEMPLATE.md` and `RULE_EVALUATION_SPEC.md` each contain the same 27 unique IDs; symmetric difference is empty. Fixture and test-plan IDs are all subsets. Verified programmatically.
- **Status consistency:** All backlog/plan/index items are `pending`; no item is incorrectly marked complete; review gate status is `READY FOR REVIEW` with reviewer `TBD`.
- **Licenses / security claims (web-verified against primary sources):**
  - Qwen2.5-7B-Instruct — **apache-2.0 confirmed** (HF model card). Note: the candidate correctly picked a 7B size; other Qwen2.5 sizes (3B, 72B) are under the non-Apache Qwen license, so the specific model choice matters and is right.
  - intfloat/multilingual-e5-small — **MIT confirmed** (HF model card); explicitly supports 100 languages and **benchmarks Indonesian (`id`) retrieval** on Mr. TyDi, which substantiates the "Indonesian-ready, not English-only" claim.
  - Docling — **MIT confirmed** (GitHub, LF AI & Data / IBM); confirms local/air-gapped execution and native Haystack integration, both claimed.
  - Not independently re-fetched but well-established and correctly stated: Haystack (Apache-2.0), Qdrant (Apache-2.0), Ollama (MIT), FastAPI (MIT), Vite (MIT), SQLite (public domain). No AGPL/SSPL/non-commercial items present. All runtime licenses are permissive and commercially usable.
  - **One nuance to flag, not an error:** Qwen2.5's official model card lists ~29 languages and does not explicitly name Indonesian ("and more"). The embedding model does explicitly support Indonesian, but the *LLM's* Indonesian legal-extraction quality is genuinely unverified — which is exactly what the pack already declines to claim (`ADR-008`, `PART2_REQUIREMENTS.md:27`). Alignment is correct; just do not upgrade this to a production claim.
- **No fabricated statistics found.** No spurious CVE, star count, commit timestamp, or benchmark number appears in the pack. The "Verified Primary Sources" list in `TECH_STACK_AND_LICENSES.md:27-40` points to real, correct URLs.

## Required Corrections

Prioritized; documents that must change together are grouped.

1. **(High, A-H1/D-05/D-08)** Add a gate condition that the live hosted demo runs Qwen2.5-7B via Ollama, or requires a recorded egress-blocked local-model run of the fixture. Update together: `ARCHITECTURE.md` (Deployment Modes), `CASE_STUDY_BASELINE.md` (Known Interpretation Risk), `OPEN_DECISIONS.md` (D-05/D-08), `EXECUTION_PLAN_48H.md` (stop conditions), `REVIEW_GATE.md`.
2. **(High, A-H3)** Define non-contract / zero-clause / non-applicable behavior. Update together: `WORKFLOW_SPEC.md`, `API_CONTRACT.md` (new error code), `OUTPUT_SCHEMA.md`, `DEFENSE_PLAYBOOK_TEMPLATE.md` (evaluation-order step 1 outcome), `TEST_AND_ACCEPTANCE_PLAN.md`.
3. **(High, A-H2)** Require one live local-model fixture pass plus recorded 3-run variance; ensure fixture confidences sit clear of 0.60. Update together: `TEST_AND_ACCEPTANCE_PLAN.md`, `DEMO_FIXTURE_SPEC.md`, `DEMO_RUNBOOK.md`.
4. **(Medium, A-M4)** Pin the low-confidence single-vs-double-finding rule. Update together: `DEFENSE_PLAYBOOK_TEMPLATE.md:100`, `RULE_EVALUATION_SPEC.md:49-54`, `TEST_AND_ACCEPTANCE_PLAN.md`.
5. **(Medium, A-M3)** Add status↔current_stage mapping table to `OUTPUT_SCHEMA.md` (or `WORKFLOW_SPEC.md`).
6. **(Medium, A-M2)** Qualify or mark provisional the 120 s/20-page target in `NON_FUNCTIONAL_REQUIREMENTS.md`.
7. **(Low, A-L1/A-L2/A-L3)** Reconcile `synthetic_data_only` (add to `DATA_MODEL.md` or drop from `API_CONTRACT.md`), declare canonical `playbook_id` in `DEFENSE_PLAYBOOK_TEMPLATE.md`, and unify version conventions.
8. **(Low, A-L4)** Add a note (or `AUD-003`) documenting AUD-001's dual missing/deviation role.
9. **(Medium, A-M1)** Add a stop-condition note preferring "simpler local path" over "switch live demo to cloud."

Accepted/proposed decisions are represented consistently across `OPEN_DECISIONS.md`, `ARCHITECTURE_DECISIONS.md`, and `AGENT_HANDOFF.md`; the only accepted-vs-proposed item needing attention is D-08 (couple it to the A-H1 guardrail).

## Final Recommendation

**PASS WITH CONDITIONS.**

The review gate should pass on the conditions that: (1) the live hosted demo is committed to running the open-source local model, or a recorded egress-blocked local run is a required demo artifact (A-H1/A-H2); (2) non-contract/zero-clause behavior is specified before the demo accepts arbitrary uploads (A-H3); and (3) scaffold-blocking decisions D-01, D-02, D-12 are formally accepted. The remaining items are Medium/Low precision fixes that do not block starting the P0 vertical slice.

I did **not** find this to be free of material issues, so I am not stating "no blocking discrepancies were found." However, I want to be clear that the issues are correctness/fidelity and edge-case gaps, **not** the fabricated-source or internal-contradiction problems seen earlier in this project — on independent verification the pack's structural integrity, rule logic, and license claims held up.

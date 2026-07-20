# Part 2 Change Control

## Enforcement Rule
If any implementation file changes, update the relevant Part 2 spec files in the same change set.

## Files That Must Stay in Sync
Paths below are relative to the repo root (`legal-contract-review-ai/`). All listed files
live under `docs/` except `README.md`, which is at the repo root.

- `CHANGE_CONTROL.md`
- `MASTER_INDEX.md`
- `README.md`
- `AGENT_HANDOFF.md`
- `PLAN.md`
- `CASE_STUDY_BASELINE.md`
- `PART2_REQUIREMENTS.md`
- `OPEN_DECISIONS.md`
- `ARCHITECTURE_DECISIONS.md`
- `TECH_STACK_AND_LICENSES.md`
- `REPOSITORY_STRATEGY.md`
- `ARCHITECTURE.md`
- `NON_FUNCTIONAL_REQUIREMENTS.md`
- `WORKFLOW_SPEC.md`
- `MODEL_AND_PIPELINE_CONTRACT.md`
- `DATA_MODEL.md`
- `OUTPUT_SCHEMA.md`
- `API_CONTRACT.md`
- `UI_SPEC.md`
- `DEFENSE_PLAYBOOK_TEMPLATE.md`
- `RULE_EVALUATION_SPEC.md`
- `PROMPT_SPEC.md`
- `SECURITY_AND_DATA.md`
- `DEMO_FIXTURE_SPEC.md`
- `TEST_AND_ACCEPTANCE_PLAN.md`
- `TRACEABILITY_MATRIX.md`
- `RISK_REGISTER.md`
- `IMPLEMENTATION_PHASE_PLAN.md`
- `IMPLEMENTATION_BACKLOG.md`
- `EXECUTION_PLAN_48H.md`
- `DEMO_RUNBOOK.md`
- `PRE_IMPLEMENTATION_SELF_REVIEW.md`
- `INDEPENDENT_AUDIT.md`
- `RE_AUDIT.md`
- `RECONCILIATION_AUDIT.md`
- `REVIEW_GATE.md`

## Required Update Triggers
Update the docs when any of these change:
- workflow steps
- output fields
- playbook rules
- UI screens
- API endpoints
- deployment assumptions
- scope or acceptance criteria
- architecture or dependency choices
- security controls or data handling
- tests, fixtures, or demo procedure
- model, prompt, scoring, or confidence behavior
- open decision or review-gate outcome

## Practical Rule
Before merging implementation work:
1. Check the master index.
2. Update the affected spec file(s).
3. Update `AGENT_HANDOFF.md` with completed work and the next task.
4. Confirm the plan and traceability matrix still match the implementation.
5. Re-run affected acceptance and security checks.

## Source-of-Truth Priority
When documents conflict, resolve them in this order:
1. The original case-study requirement
2. `CASE_STUDY_BASELINE.md`
3. `PART2_REQUIREMENTS.md`
4. Accepted decisions in `ARCHITECTURE_DECISIONS.md`
5. The detailed functional and technical specifications
6. `PLAN.md` and `AGENT_HANDOFF.md`

Fix any conflict immediately; do not silently choose one interpretation.

## Review-Gate Enforcement
- Before implementation, `REVIEW_GATE.md` requires explicit review approval.
- A proposed decision is not accepted merely because it appears in a recommendation.
- Review findings must be applied to all affected documents before the gate passes.
- After implementation begins, any material scope or architecture reversal returns the project to review.

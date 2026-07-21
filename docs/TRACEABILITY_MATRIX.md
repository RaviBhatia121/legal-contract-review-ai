# Part 2 Requirement Traceability

Use this matrix to prevent implementation drift.

As of P2, the "Clause extraction," "Risk classification," "Playbook deviation detection,"
and "Deterministic rule behavior" rows are executed, not just planned — see
`backend/tests/test_rule_engine.py` (27 rule predicates + aggregation),
`backend/tests/test_segmentation.py`, `backend/tests/test_attribute_extraction.py`, and the
golden-fixture assertions in `backend/tests/test_reviews_golden_path.py`.

| Requirement | Authoritative Specification | Verification |
|---|---|---|
| Original case-study wording | `CASE_STUDY_BASELINE.md` | PDF source comparison |
| Functional Legal prototype | `PART2_REQUIREMENTS.md` | Hosted golden-path demo |
| Agentic, structured, non-chat workflow | `WORKFLOW_SPEC.md` | Pipeline and API tests |
| Upload contract and annotate risks | `UI_SPEC.md`, `OUTPUT_SCHEMA.md` | End-to-end test and screenshot |
| Legal automated drafting support | `OUTPUT_SCHEMA.md`, `WORKFLOW_SPEC.md`, `UI_SPEC.md` | Approved-template `suggested_draft_clause` assertions |
| Clause extraction | `WORKFLOW_SPEC.md` | Fixture assertions |
| Empty and out-of-scope document handling | `WORKFLOW_SPEC.md`, `API_CONTRACT.md` | Typed-failure tests with no fabricated findings |
| Risk classification | `DEFENSE_PLAYBOOK_TEMPLATE.md` | Rule test cases |
| Playbook deviation detection | `DEFENSE_PLAYBOOK_TEMPLATE.md` | Missing/deviating clause tests |
| Deterministic rule behavior | `RULE_EVALUATION_SPEC.md` | Predicate unit tests |
| Pre-prompted AI actions | `PROMPT_SPEC.md`, `MODEL_AND_PIPELINE_CONTRACT.md` | Prompt contract and schema tests |
| Structured output | `OUTPUT_SCHEMA.md`, `API_CONTRACT.md` | JSON Schema validation |
| Enterprise deployment confidence | `ARCHITECTURE.md` | Architecture walkthrough |
| On-premises target | `ARCHITECTURE_DECISIONS.md`, `SECURITY_AND_DATA.md` | Config and network design review |
| Open-source commercially viable local model | `TECH_STACK_AND_LICENSES.md`, `MODEL_AND_PIPELINE_CONTRACT.md` | License check, successful egress-blocked golden-fixture run, and three-run variance record |
| Vector database specified | `ARCHITECTURE.md`, `WORKFLOW_SPEC.md` | Qdrant guidance-retrieval and outage tests |
| Vector database role visible in portal | `UI_SPEC.md`, `ARCHITECTURE.md` | Dashboard/review guidance-status tests |
| Backend orchestration specified | `ARCHITECTURE.md`, `WORKFLOW_SPEC.md` | Haystack pipeline test |
| Frontend portal specified | `UI_SPEC.md` | Hosted UI walkthrough |
| Repository delivery structure | `REPOSITORY_STRATEGY.md` | Monorepo structure and CI review |
| Indonesian-ready text handling | `PART2_REQUIREMENTS.md`, `NON_FUNCTIONAL_REQUIREMENTS.md` | Unicode preservation and optional Indonesian smoke test |
| Secure local data flow walkthrough | `ARCHITECTURE.md`, `SECURITY_AND_DATA.md` | Architecture review |
| In-app stack and secure-flow walkthrough | `UI_SPEC.md`, `ARCHITECTURE.md` | `/architecture` page and frontend tests |
| Hosted demonstration | `ARCHITECTURE.md`, `DEMO_RUNBOOK.md` | URL and health check |
| Security-conscious handling | `SECURITY_AND_DATA.md` | Security test checklist |

## Update Rule
When a requirement, specification, or acceptance test changes, update the corresponding row in the same change set.

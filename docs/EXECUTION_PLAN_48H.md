# Part 2 48-Hour Execution Plan

## Assumption
Two focused build days. Time boxes are elapsed engineering hours and may shift, but the order does not.

## Day 1: Vertical Slice

| Time Box | Outcome |
|---|---|
| Hours 0-2 | Monorepo scaffold, Docker Compose, React/Vite, FastAPI, SQLite, approved job runner, health/config endpoints |
| Hours 2-4 | Generate synthetic DOCX/PDF and expected JSON; secure upload validation and review job lifecycle |
| Hours 4-6 | Docling parsing of the generated fixture PDF and DOCX |
| Hours 6-9 | Schema-valid fixed result, polling UI, findings screen, error states |
| Hours 9-10 | API/UI golden-path tests and Day 1 stabilization |

Day 1 exit criterion: hosted-shaped application works end to end with a clearly identified fixture result and no model claim.

## Day 2: Real Pipeline and Deployment

| Time Box | Outcome |
|---|---|
| Hours 0-3 | Haystack components, local model adapter, prompts, validated clause/attribute extraction |
| Hours 3-5 | Versioned rule engine, missing clauses, aggregation, SQLite persistence |
| Hours 5-7 | Multilingual E5 embeddings and Qdrant supplemental-guidance retrieval with safe fallback |
| Hours 7-9 | Hosted provider adapter if selected, admin configuration, Demo mode controls |
| Hours 9-11 | Security tests, repeatability run, egress/local-path verification, bug fixes |
| Hours 11-12 | Deploy, smoke test, evidence capture, architecture walkthrough, runbook completion |

## Scope-Cut Order
If behind schedule, cut in this order without violating the case study:
1. Historical review list and deletion UI; retain API-level lifecycle.
2. Multiple cloud providers; implement only the selected demo provider plus Docker Ollama.
3. Compliant-findings expansion and advanced filters.
4. Similar-clause history; retain Qdrant supplemental playbook-guidance retrieval only.
5. DOCX demo path if PDF is fully functional; if cut, update the API, UI, tests, and runbook in the same change and disclose the limitation.

Do not cut structured output, evidence, deterministic rules, local-model path, synthetic-data control, upload security, or hosted working URL.

## Stop Conditions
- If Docling does not parse the fixture reliably within two hours, use a simpler local parser behind the same interface and record the decision.
- If Haystack integration blocks the vertical slice, keep the explicit pipeline interface, complete the workflow, and record Haystack as the target orchestration rather than pretending it is active.
- If local model quality fails the expected rule outcomes, first simplify the bounded prompt, tune only the synthetic fixture wording where it is near the confidence boundary, then test a larger permissively licensed local model behind the same adapter. The PoC starts with Docker Ollama + `qwen3:4b`; do not switch to a non-permissive model just because it is lighter.
- A hosted provider may still power the disclosed synthetic Demo mode, but it cannot replace the mandatory successful local-model verification. If no local model passes, record the case-study requirement as unmet rather than claiming completion.

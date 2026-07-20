# Part 2 Open Decisions

These decisions do not block documentation review. They must be accepted or changed before the related implementation begins.

| ID | Decision | Recommendation | When Needed | Status |
|---|---|---|---|---|
| D-01 | Frontend framework | React + TypeScript + Vite | Scaffold | Accepted |
| D-02 | Prototype result persistence | SQLite with repository boundary | Backend scaffold | Accepted |
| D-03 | Local PoC reference LLM | Docker-based Ollama with `qwen3:4b`; larger local models may be tested if quality is insufficient | Model integration | Accepted |
| D-04 | Embedding model | intfloat/multilingual-e5-small | Qdrant integration | Accepted |
| D-05 | Hosted demo model provider | Stays open. P7's hosted demo is deterministic-only — no model provider is reachable from the hosted environment, so no cloud adapter was implemented or needed | Hosted integration | Open |
| D-06 | Hosted authentication | Reverse-proxy access restriction or simple authenticated app session | Deployment | Accepted; implemented in P7 as an app-level HTTP Basic Auth middleware (`DemoBasicAuthMiddleware`), active only when `deployment_mode: demo` |
| D-07 | Hosting platform | Use a container host that supports private services, persistent disk, TLS, and server-side secrets | Deployment | Accepted in P7: Render, Docker Web Service (`render.yaml`, `backend/Dockerfile.hosted`). Persistence: **ephemeral SQLite** on the default free plan (no persistent disk on that tier) — a disclosed demo-only exception, not production-equivalent. A paid plan with a mounted disk (or Render Postgres) is the documented upgrade path if hosted persistence is ever needed; not adopted for this PoC. See `docs/SECURITY_EVIDENCE.md` section 10. |
| D-08 | Cloud-demo exception | Permit proprietary provider only for synthetic Demo mode; retain verified local path | Already agreed in planning; reconfirm at review | Accepted |
| D-09 | Qdrant role | Rank supplemental guidance/examples; always evaluate the complete applicable rule set | Pipeline | Accepted |
| D-10 | Compliant findings visibility | Show them collapsed by default to demonstrate coverage without noise | UI | Accepted |
| D-11 | Demo credential lifecycle | Environment bootstrap plus write-only in-memory admin override; enterprise target uses approved secret manager | Configuration implementation | Accepted |
| D-12 | Prototype job runner | Bounded in-process FastAPI background executor for one-instance PoC; dedicated queue/worker in enterprise target | Backend scaffold | Accepted |

## Approval Method
During specification review, change `Proposed` to `Accepted` or record the replacement. Accepted architecture decisions must also be copied into `ARCHITECTURE_DECISIONS.md`.

## Remaining Open Decisions
- D-05 hosted demo model provider remains open by design — the hosted demo
  is deterministic-only (P7), so this decision was never forced. It can
  still be selected later if a real hosted model integration is ever
  pursued.

D-07 is accepted as of P7 — see the table above and `docs/SECURITY_EVIDENCE.md` section 10.

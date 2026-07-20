# Part 2 Solution Architecture

## Logical Flow
1. Browser uploads a synthetic contract to the backend.
2. The backend validates the file and creates a review job.
3. The parser extracts text and page references (P1: `pypdf`/`python-docx`; Docling is the
   target parser once P6 model-artifact pre-provisioning exists — see
   `TECH_STACK_AND_LICENSES.md`).
4. Haystack executes the fixed review pipeline.
5. The application rejects empty or out-of-scope documents with a typed failed result before legal-rule evaluation.
6. The model adapter performs bounded clause segmentation and classification.
7. The application loads all applicable clause-type rules.
8. The model adapter extracts only the normalized attributes required by the complete rule set.
9. Application rules evaluate attributes and assign findings, severity, explanations, and actions.
10. Schema validation rejects or repairs malformed intermediate model output and validates the final result.
11. **As of P4:** for each triggered rule, the application queries Qdrant (real local
    embeddings via Docker Ollama, `rule_id`-filtered) for supplemental guidance and attaches
    it to the finding. This runs strictly after step 9 — findings, severities, and overall
    risk are already final; retrieval can only add a `guidance` list, never change them. If
    Qdrant or the embedding model is unreachable, this step degrades to
    `retrieval_mode: degraded_full_rules` and `guidance: []` without failing the review.
12. SQLite stores the immutable result, provenance, and any retrieved guidance.
13. The frontend polls the API and renders findings, evidence, recommended actions, and
    supplemental guidance where available.

## Component Boundaries

| Component | Responsibility | Must Not Do |
|---|---|---|
| React/Vite frontend | Upload, job status, findings, configuration UI | Process documents or expose secrets |
| FastAPI | Validation, authorization boundary, job/API lifecycle | Return provider credentials |
| PoC job runner | Execute bounded review jobs in the backend process | Claim multi-instance durability or production queue semantics |
| Parser (P1: `pypdf`/`python-docx`; target: Docling, P6+) | Local PDF/DOCX parsing | Call external parsing services |
| Haystack | Execute explicit pipeline stages | Create a conversational agent loop |
| Model adapter | Normalize provider calls and structured responses | Decide application routing or persistence |
| Rule engine | Apply playbook rules and aggregate risk | Depend on free-form chat output |
| Qdrant (P4, in use) | Rank supplemental playbook guidance, queried post-processing after rule evaluation (`backend/app/services/guidance_retrieval.py`) | Exclude applicable rules, assign risk, or become the result source of truth — verified live: retrieval-on vs retrieval-off produce identical rule outcomes |
| SQLite result store | Persist review status, structured findings, and provenance | Store plaintext credentials or original uploads |

## Deployment Modes

### Hosted Demo
- Publicly reachable URL with required authentication or access restriction.
- Approved cloud model may be configured for speed.
- Synthetic contracts only.
- Clearly labelled `Demo mode`.
- Original uploads deleted after processing; review records expire after 24 hours.

### Target Enterprise
- Deployed inside the client-controlled environment.
- Docker-based Ollama for PoC validation, or an equivalent local model endpoint in the enterprise target.
- Local parsing, storage, vector database, backend, and frontend.
- No external model or document-processing calls.
- Pre-provisioned parser, embedding, and LLM artifacts with egress denied at runtime.

## Trust Boundaries
- Public browser to TLS ingress: untrusted network and user input.
- Ingress to backend: authenticated application requests only.
- Backend to model provider: server-side credentials and allowlisted destination.
- Backend to parser (P1: `pypdf`/`python-docx`): local file content in an isolated processing boundary.
- Backend to Qdrant/SQLite: private service network; never exposed to the browser.
- Contract content to model: untrusted evidence with no tools or instruction authority.

## Scope Guardrails
- No chatbot.
- No contract drafting or redlining.
- No autonomous legal decision.
- No production claim based solely on the hosted demo.
- Cloud processing is a disclosed Demo-mode exception, not the production design.
- Final requirement evidence includes a successful egress-blocked Docker Ollama/Qwen run; cloud execution cannot substitute for it.

## Prototype Job Execution
The proposed PoC baseline uses a bounded in-process background executor in a single backend instance. Active jobs that are interrupted by restart transition to `failed` during recovery. The enterprise target separates API and workers through a durable internal queue. This remains proposed decision D-12 until review.

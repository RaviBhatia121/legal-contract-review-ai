# Part 2 Technology and License Record

## Proposed Planning Baseline

Detailed specifications are reconciled against this baseline. Items marked `Proposed` in `OPEN_DECISIONS.md` remain subject to stakeholder approval before their implementation begins.

| Layer | Selection | License Position | Purpose |
|---|---|---|---|
| Frontend | React + TypeScript + Vite | MIT | Small single-page intranet portal |
| Backend | FastAPI + Pydantic | MIT | API, validation, job lifecycle, provider boundary |
| Orchestration (P3, in use) | Haystack 2.31 (`haystack-ai`) | Apache-2.0 | Explicit async pipeline components wrapping the Ollama adapter |
| HTTP client (P3, in use) | httpx | BSD-3-Clause | Ollama REST API calls from the model adapter |
| Parsing (P1, in use) | pypdf + python-docx | BSD-3-Clause / MIT | Local PDF and DOCX text extraction |
| Parsing (deferred target) | Docling | MIT | Local PDF and DOCX extraction once model-artifact pre-provisioning exists (P6+) |
| Vector database (P4, in use) | Qdrant | Apache-2.0 | Supplemental playbook guidance retrieval, queried post-processing |
| Vector database client (P4, in use) | `qdrant-client` 1.12 | Apache-2.0 | Async Qdrant SDK used by `backend/app/services/guidance_retrieval.py` |
| Result store | SQLite | Public domain | Prototype jobs, metadata, and structured results |
| Model runtime | Ollama on shared on-prem VM | MIT | On-premises model serving without running a heavy local model on the demo laptop |
| Current demo LLM | `qwen3.6:35b` | Apache-2.0 (Qwen3 family) | Shared-VM structured extraction/classification for browser demo validation |
| Historical P3 validation LLM | Qwen3-4B (`qwen3:4b`) | Apache-2.0 | Earlier Docker-local validation evidence; no longer the current demo default |
| Optional stronger LLM | Qwen2.5-7B-Instruct | Apache-2.0 | Larger fallback if the lightweight model cannot pass the golden fixture |
| Embeddings (P4, in use) | `intfloat/multilingual-e5-small`, served via `qllama/multilingual-e5-small` (Ollama GGUF) | MIT | Local guidance-corpus and query embeddings for Qdrant retrieval |
| Packaging | Docker Compose | Apache-2.0 | Repeatable local and hosted deployment |
| Fixture generation (build-time only, not runtime) | reportlab | BSD-3-Clause | Synthetic PDF fixture rendering in `scripts/generate_fixtures.py`; installed via the `fixtures` optional dependency group, not part of the shipped backend image |

## Recommended Selection Rationale
- Use React/Vite instead of Next.js because the product is an authenticated application backed by FastAPI and does not need server-side rendering.
- Use SQLite for the prototype because review volume is low and the result structure is simple. The boundary must permit PostgreSQL later.
- Use Qdrant to rank supplemental guidance and examples. Application code always evaluates the complete applicable rule set.
- Use only stable Haystack components; do not depend on `haystack-experimental`.
  **P3 note:** `haystack-experimental` is pulled in as a hard transitive dependency of
  `haystack-ai` itself — this rule is about not *importing* experimental components in our
  own code (we don't), not about the package being absent from the dependency tree.
- Run Docling locally with pre-fetched artifacts in the on-premises target.
- **P1 update:** Docling was spiked in P1 and found to unconditionally attempt an
  HuggingFace Hub model download for its layout model even with `do_ocr=False` set and a
  purely text-native PDF; there is no artifact pre-provisioning story until P6. P1 therefore
  uses `pypdf` + `python-docx`, both verified to work fully offline with no model
  dependency. Docling remains the intended parser once P6 artifact pre-provisioning exists;
  this is a deferred re-adoption, not a permanent replacement.
- **P3 spike:** unlike Docling, `haystack-ai` installed cleanly (~6s, ~136MB, no
  torch/transformers) and custom async components verified working end to end against a
  mocked Ollama HTTP server in well under a second. Go decision; no fallback needed. Only
  `ollama` has an implemented adapter — Anthropic/OpenAI/Gemini remain unimplemented behind
  the same `ModelAdapter` interface (P5/D-05), never silently introduced.
- **P3 local-model decision update:** use Docker-based Ollama with `qwen3:4b` for PoC
  verification. This keeps the runtime isolated/removable and proves the orchestration,
  schema validation, and deterministic rule evaluation without requiring a heavier model.
  `qwen2.5:3b-instruct` was considered but rejected for this case-study baseline because
  its model card lists `qwen-research`, not Apache-2.0. `llama3.2:3b` was also not selected
  because the Meta Llama license is not one of the preferred MIT/Apache/BSD-style licenses.
- **P8 shared-VM runtime update:** current local browser demos use the existing on-prem
  Ollama VM at `http://<ollama-vm-ip>:11434` with `qwen3.6:35b`, because laptop-local model
  pulls/runtime proved too heavy and slow for repeated manual demos. This is still
  local/on-premises, not a cloud API. The laptop-local Compose `ollama` service is retained
  only as an opt-in fallback profile. The Qwen3 family is documented by QwenLM as Apache-2.0
  for open-weight models; verify the exact pinned artifact/model card again before any
  production procurement, but the PoC model-family license posture is commercially viable.
- **P4 embedding-model spike (go/no-go — the already-accepted `intfloat/multilingual-e5-small`
  was never silently replaced):** `ADR-005`/`D-04` accepted `multilingual-e5-small`
  (MIT) but never verified it was actually servable through this project's Docker-Ollama-only
  infrastructure — its official Hugging Face repo is a raw `sentence-transformers` model, not
  GGUF, and Ollama's `hf.co/` direct-pull path rejected it outright
  (`400: Repository is not GGUF or is not compatible with llama.cpp`). Searched for a
  community GGUF re-packaging (`WebSearch`, see `qllama/multilingual-e5-small` on
  ollama.com) and verified it live: pulled cleanly (131MB, f16), and `POST
  /api/embeddings` returned deterministic 384-dimension vectors (identical on repeat calls,
  matching `intfloat/multilingual-e5-small`'s known embedding size) — confirmed against the
  same Docker Ollama container P3 already uses. **Spike passed; no fallback substitution was
  needed.** The underlying model weights are unchanged and remain MIT-licensed — GGUF
  quantization/re-packaging by a third party does not alter that license, and MIT explicitly
  permits redistribution and modification. This is the same disciplined go/no-go pattern as
  the P1 Docling rejection and the P3 Haystack go-decision: verify before adopting, and
  document the result either way rather than asserting an untested model choice works.

## Verified Primary Sources
Validated on 2026-07-18 (P0/P1); Haystack/httpx spiked and confirmed 2026-07-19 (P3);
Qdrant/embedding-model spike confirmed 2026-07-19 (P4):
- Haystack repository and Apache-2.0 identifier: https://github.com/deepset-ai/haystack
- Haystack security policy: https://github.com/deepset-ai/haystack/blob/main/SECURITY.md
- httpx repository and BSD-3-Clause license: https://github.com/encode/httpx
- Docling repository and MIT license: https://github.com/docling-project/docling
- Docling offline operation: https://docling-project.github.io/docling/faq/
- pypdf repository and BSD-3-Clause license: https://github.com/py-pdf/pypdf
- python-docx repository and MIT license: https://github.com/python-openxml/python-docx
- reportlab repository and BSD-3-Clause license: https://github.com/MrBitBucket/reportlab-mirror
- Qdrant repository and Apache-2.0 license: https://github.com/qdrant/qdrant
- Qdrant self-hosted security guidance: https://qdrant.tech/documentation/security/
- Ollama MIT license: https://github.com/ollama/ollama/blob/main/LICENSE
- Ollama security policy: https://github.com/ollama/ollama/blob/main/SECURITY.md
- Qwen3 repository license statement: https://github.com/QwenLM/Qwen3
- Qwen3 Apache-2.0 license example: https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507/blob/main/LICENSE
- Qwen3-4B Apache-2.0 model: https://huggingface.co/Qwen/Qwen3-4B
- FastAPI MIT license: https://github.com/fastapi/fastapi/blob/master/LICENSE
- Vite MIT license: https://github.com/vitejs/vite
- Qwen2.5-7B-Instruct Apache-2.0 model: https://huggingface.co/Qwen/Qwen2.5-7B-Instruct
- Multilingual E5 small MIT model: https://huggingface.co/intfloat/multilingual-e5-small
- Community GGUF re-packaging used to serve it via Docker Ollama:
  https://ollama.com/qllama/multilingual-e5-small
- `qdrant-client` repository and Apache-2.0 license: https://github.com/qdrant/qdrant-client

## Security Findings Affecting Design
- Haystack treats input validation, SSRF prevention, and document prompt-injection defenses as application responsibilities.
- Haystack serialized pipelines and snapshots are trusted code-like artifacts and must never be loaded from user input.
- Qdrant self-hosted deployments are not secure by default; authentication, binding, TLS, and network controls must be configured.
- Docling can operate offline, but model artifacts must be pre-fetched and supplied locally.
- Runtime license compatibility does not automatically cover every transitive dependency or model artifact.
- `haystack-ai` pulls in `posthog` (telemetry client) transitively; disabled via
  `HAYSTACK_TELEMETRY_ENABLED=False`, set before any `haystack` import (see
  `SECURITY_AND_DATA.md`).

## Implementation Enforcement
- Pin exact package, container, and model revisions in lockfiles or deployment manifests.
- Generate a software bill of materials and run license scanning before the hosted release.
- Reject AGPL, SSPL, non-commercial, research-only, or unknown-license runtime dependencies unless explicitly reviewed and replaced.
- Re-check licenses at the pinned revision; this file is a selection record, not legal advice.

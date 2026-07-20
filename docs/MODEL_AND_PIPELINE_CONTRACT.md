# Part 2 Model and Pipeline Contract

Implemented as of P3: Task 1 (`backend/app/model_adapter/ollama_adapter.py`
via `backend/app/services/haystack_pipeline.py`'s `ClauseClassifierComponent`)
and Task 2 (`AttributeExtractorComponent`). Only Ollama is wired — cloud
providers are not implemented, per `TECH_STACK_AND_LICENSES.md` and D-05.
This path is opt-in (`PART2_CLAUSE_INTELLIGENCE_MODE=model`); the default
everywhere is P2's deterministic fixture-oriented path
(`backend/app/services/rule_engine.build_deterministic_clause_inputs`), kept
as the fallback/test-double — see `IMPLEMENTATION_PHASE_PLAN.md` P3 notes.

## Principle
The workflow is deterministic in structure, validation, and scoring. Model generation is probabilistic and must not be described as mathematically deterministic.

Reproducibility controls:
- fixed pipeline order
- versioned prompts and playbook
- temperature `0` where supported
- constrained JSON output
- schema validation at every model boundary
- no model tools or autonomous routing
- deterministic final rule evaluation and risk aggregation

## Reference Models
- Local PoC LLM: `qwen3:4b`, Apache-2.0, served through Docker-based Ollama.
- Optional stronger local validation candidate: `Qwen2.5-7B-Instruct`, Apache-2.0, if the lightweight model fails the golden fixture.
- Local embeddings: `intfloat/multilingual-e5-small`, MIT; selected to avoid an English-only retrieval path.
- Hosted demo provider: unresolved and isolated behind the same adapter.

`qwen2.5:3b-instruct` is intentionally not the PoC reference despite being lightweight,
because its model card currently lists `qwen-research`, not Apache-2.0. `llama3.2:3b` is
also not the reference because the Meta Llama license is not one of the preferred
MIT/Apache/BSD-style licenses for this case study.

## Model Tasks

### Task 1: Clause Segmentation and Classification
Input:
- trusted task instruction
- untrusted extracted document text with page/section metadata
- closed clause-type enumeration

Output:
- clause identifier
- clause type
- section/page reference
- verbatim evidence text
- confidence from `0` to `1`

The model must not invent missing text or infer a clause as present without evidence.

### Task 2: Clause Attribute Extraction
Input:
- one clause
- requested attributes for its clause type

Output:
- normalized attributes only, such as approval required, retention period, liability cap, or governing location
- supporting evidence spans
- `unknown` when not stated

## Application-Owned Tasks
- file validation
- pipeline routing
- required-clause completeness
- playbook rule evaluation
- severity assignment
- overall-risk aggregation
- deviation text from versioned rule templates
- recommended actions from the playbook
- authorization and storage

## Prompt-Injection Boundary
Document text is enclosed as untrusted evidence and is never concatenated into system instructions. Prompts explicitly state that text inside the evidence block is content to analyze, not instructions. No task exposes tools, URLs, filesystem access, or secrets to the model.

## Language Handling
- Detect or record the source language without translating the evidence.
- Preserve verbatim Unicode evidence.
- Return the same language for extracted titles where possible; structured clause types and attributes remain schema enums.
- The English golden fixture is authoritative for MVP acceptance. Indonesian quality is not claimed until separately evaluated.

## Failure Handling
- One structured-output repair attempt is allowed using validation errors only.
- If repair fails, mark the review `failed`; do not silently return partial success.
- Classifications from `0.60` to `0.79` are evaluated with `needs_review: true`. Classifications below `0.60` emit `REV-001` and do not establish clause presence.
- Provider timeouts and safety refusals produce typed errors without document text in logs.

## Versioning
Every result records model provider, model name, model revision where available, prompt version, playbook version, parser version, and pipeline version.

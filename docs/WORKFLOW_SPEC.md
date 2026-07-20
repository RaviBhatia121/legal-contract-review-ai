# Part 2 Workflow Specification

## Workflow
`upload -> validate -> parse -> check reviewable text -> segment/classify -> check applicability -> load rules/retrieve guidance -> extract attributes -> evaluate all applicable rules -> validate -> persist -> render`

This is a fixed application pipeline, not an autonomous agent loop.

**P3 correction to this ordering:** the original design put the full
applicability check before segment/classify. Real applicability (is this
document actually a services-agreement-like contract?) requires
classification output, which doesn't exist yet at that point. As of P3,
applicability is split: the text-length floor (`NO_REVIEWABLE_TEXT`) still
runs before classification (nothing to classify otherwise); the real
services-agreement-scope check (`DOCUMENT_NOT_APPLICABLE`) now runs
immediately after classification, using its output. This is a source-agnostic
check — it runs identically whether classification came from the P2
deterministic path or the P3 model-assisted path. See stages 3 and 4 below
and `backend/app/services/applicability.py`.

## Stages

### 1. Upload and Validate
- Accept one PDF or DOCX up to 15 MB and 100 pages.
- Verify size, extension, detected MIME type, and encryption status.
- Generate a server-side file path and SHA-256 digest.
- Create an immutable review identifier with status `queued`.
- Set `current_stage` to `queued` after job creation.

Failure: typed rejection; no parsing or model call.

### 2. Parse Locally
- P1 uses `pypdf` (PDF) and `python-docx` (DOCX), not Docling: an offline spike found
  Docling's default pipeline unconditionally attempts an HuggingFace Hub model download
  even with OCR disabled, which has no artifact pre-provisioning story until P6 (see
  `TECH_STACK_AND_LICENSES.md`). Docling remains the intended parser once that
  pre-provisioning exists.
- Extract text; page references where available. Structural extraction (headings, reading
  order) is not implemented in P1 — clause segmentation is P2/P3 scope.
- P1 does not implement real language detection (no library was approved this phase);
  `document_language` is `"en"` for any non-empty extracted text and `"unknown"` for empty
  text. Real detection is deferred.
- Set status `parsing`.
- Set `current_stage` to `parsing_document`.

Failure: delete temporary artifacts and return `DOCUMENT_PARSE_FAILED`.

### 3. Check Reviewable Text
- Set status `analyzing`.
- Set `current_stage` to `checking_applicability`.
- Reject parsed documents with no usable review text as `NO_REVIEWABLE_TEXT`. A text-length
  floor (`backend/app/services/applicability.has_reviewable_text`), unchanged since P1 —
  this check needs no classification and stays here.
- Do not fabricate missing-clause findings when applicability has not been established.

Failure: persist a typed failed result and delete temporary artifacts; do not continue to clause classification or rule evaluation.

### 4. Segment and Classify, then Check Applicability
- Set status `analyzing`.
- Set `current_stage` to `classifying_clauses`.
- Produce `ClauseInput`s (`backend/app/services/rule_engine.py`) via one of two
  interchangeable paths, selected by `Settings.clause_intelligence_mode`
  (default `"deterministic"` everywhere):
  - **Deterministic (default/fallback/test-double):** `backend/app/services/segmentation.py`
    performs fixture-oriented heading/sub-clause segmentation over `Review.parsed_text` — it
    recognizes one known synthetic contract's "Section N. Title" / "N.M" numbering
    convention, not general contract structure.
  - **Model-assisted (P3, opt-in via `PART2_CLAUSE_INTELLIGENCE_MODE=model`):**
    `backend/app/services/clause_intelligence.py` runs a Haystack pipeline
    (`haystack_pipeline.py`) over a general, non-fixture-tuned block splitter
    (`block_splitter.py`) and the Ollama adapter (`model_adapter/ollama_adapter.py`),
    implementing PROMPT_SPEC.md's P-01/P-02 tasks. Only Ollama is wired; cloud providers
    are not implemented (P5/D-05).
- Preserve verbatim evidence and classification confidence.
- Never accept document text as workflow instructions.
- **Real applicability check runs here, after classification, not before:** reject
  documents outside the configured services-agreement scope as `DOCUMENT_NOT_APPLICABLE`
  when fewer than 2 required clause types were classified at or above the confidence floor
  (`backend/app/services/applicability.is_applicable`). This runs identically regardless of
  which path produced the `ClauseInput`s — see the P3 workflow-order correction above.
- On `ModelTimeoutError`/`ModelOutputInvalidError`/`ProviderUnavailableError` from the model
  path: typed failure (`MODEL_TIMEOUT`/`MODEL_OUTPUT_INVALID`/`PROVIDER_UNAVAILABLE`), no
  partial success persisted.

Failure: persist a typed failed result and delete temporary artifacts; do not continue to rule evaluation.

### 5. Load Rules
- Set `current_stage` to `checking_playbook`.
- Loads the complete versioned rule set from `playbooks/defense-services-v1.json` via
  `backend/app/playbook/loader.py`. The complete clause-type rule set is always evaluated —
  no rule is ever excluded by retrieval (see stage 7's P4 note).
- **P4 correction to this stage's original name:** guidance retrieval does not happen here.
  It was originally planned as part of this stage, but the implementation queries Qdrant
  *after* rule evaluation (stage 7), once real findings and rule_ids exist to key the lookup
  on — querying before evaluation would have nothing meaningful to filter by. This mirrors
  the same kind of disclosed stage-order correction P3 made for `DOCUMENT_NOT_APPLICABLE`.

### 6. Extract Attributes
- Set `current_stage` to `extracting_attributes`.
- **Deterministic path:** `backend/app/services/attribute_extraction.py` extracts
  normalized attributes via fixture-tuned phrase matching.
- **Model-assisted path (P3):** the Haystack `AttributeExtractorComponent` calls the model
  per PROMPT_SPEC.md's P-02, then `backend/app/schemas/clause_attributes.py` normalizes and
  validates the result against `RULE_EVALUATION_SPEC.md`'s attribute table — any missing or
  malformed attribute is coerced to `unknown`, never silently defaulted to compliant.
- Both paths produce the same `ClauseInput` shape; unrecognized wording correctly yields
  `unknown` attributes and low confidence (see `DEFENSE_PLAYBOOK_TEMPLATE.md`'s Confidence
  Handling), never a false compliant result.
- Preserve supporting evidence spans.

### 7. Evaluate Rules
- Set `current_stage` to `evaluating_rules`.
- `backend/app/services/rule_engine.evaluate_clauses` applies every rule for the classified
  clause type in ascending rule-ID order, detects missing required clauses, applies
  confidence-banding (`REV-001`) and the `AUD-001` dual-purpose (missing vs. deviation)
  behavior, and deduplicates. This is unchanged and identical for both extraction paths —
  rule IDs, severities, and recommended actions come from the playbook data, never chosen by
  the extractor or the model. `Finding.source` is `"model_assisted_rule"` for evidence-based
  findings from the model path (`"rule"` for the deterministic path); missing-clause
  findings are always `"rule"` since they have no clause evidence.
- **P4: retrieve supplemental guidance, strictly after the above.** For each distinct
  triggered `rule_id`, `backend/app/services/guidance_retrieval.GuidanceService` queries
  Qdrant (a real vector search filtered to that `rule_id`, using a local embedding of the
  rule's trigger text computed via Docker Ollama) and attaches the result to
  `Finding.guidance`. `rule_engine.py` itself is not called again and has no awareness this
  happens — retrieval can only add a `guidance` list to an already-final finding, never
  change its `rule_id`, `risk_label`, `finding_type`, or any other field. If Qdrant or the
  embedding model is unreachable, this sets `retrieval_mode: degraded_full_rules` and
  `guidance: []` on every finding, without failing the review — verified live: retrieval-on
  and retrieval-off runs of the same document produce identical rule outcomes.

### 8. Validate and Aggregate
- Set status `validating`.
- Set `current_stage` to `validating_result`.
- Validate all model boundaries and final output.
- Calculate counts and overall risk deterministically.
- Allow one structured-output repair attempt before failing.

### 9. Persist and Clean Up
- Store immutable review metadata, findings, retrieved guidance, and provenance in SQLite.
- Delete the uploaded original immediately after processing in hosted Demo mode.
- **P4 correction:** the original plan anticipated per-review vectors in Qdrant that would
  need removal on review expiry/deletion. The implemented design stores no review-specific
  or contract-derived data in Qdrant at all — only a static, admin-managed guidance corpus
  (`playbooks/guidance-v1.json`) shared across every review. Retrieved guidance for a given
  review is a copy stored in SQLite (`Finding.guidance_json`), deleted with the review like
  any other finding field; there is nothing Qdrant-side to remove per review. This is a
  stronger data-boundary than originally planned, not a gap.

### 10. Render
- Set status `completed` only after persistence succeeds.
- Show summary, findings, evidence, rules, recommendations, and provenance.
- Collapse Low/compliant items by default.

## State Transitions
- `queued -> parsing -> analyzing -> validating -> completed`
- Any active state may transition to `failed`.
- `completed` and `failed` are terminal and immutable.
- If proposed decision D-12 is accepted, PoC startup recovery changes any interrupted active job to `failed` with `JOB_INTERRUPTED`.

## Reproducibility
Each review records the exact pipeline, playbook, prompt, parser, model, and deployment-mode identifiers. A repeated run is a new review; exact wording may vary, but rules, severities, and aggregation must remain stable for equivalent extracted attributes.

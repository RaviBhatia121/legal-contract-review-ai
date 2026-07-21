# Part 2 Data Model

## Entities

### Review
- `id`: opaque UUID
- `document_name`: sanitized display name
- `document_sha256`: integrity and duplicate reference
- `document_page_count`
- `document_language`: detected BCP 47 code such as `en` or `id`, or `unknown`
- `status`: `queued | parsing | analyzing | validating | completed | failed`
- `current_stage`: display-safe substage while active
- `overall_risk`: nullable until completed
- `created_at`, `started_at`, `completed_at`
- `error_code`, `error_message`, `error_retryable`: populated only on failure using the safe API error contract
- `pipeline_version`, `playbook_version`, `prompt_version`
- `model_provider`, `model_name`, `model_revision`: `"rule-engine"`/`"none"`/`null` in
  deterministic mode; the configured Ollama provider/model in model mode (P3)
- `mode_requested`, `mode_used`, `fallback_used`, `fallback_reason`: model-vs-rules
  provenance added after P8 so a model-unavailable review cannot be confused with
  AI-assisted output
- `deployment_mode`
- `retrieval_mode`: `qdrant | degraded_full_rules` — real as of P4 (was always
  `degraded_full_rules` before retrieval was implemented); reflects whether Qdrant/the
  embedding model answered for this review, not a user setting
- `upload_temp_path`: server-side temp-file path (P1), internal only, never serialized to
  the API; set at review creation, cleared once the temp file is deleted (success, typed
  failure, or restart recovery)
- `parsed_text`: full extracted document text (P1); as of P2, actually consumed by
  `backend/app/services/rule_engine.py` for segmentation and rule evaluation within the
  same job-runner pass. Never returned directly by the API.
- `parser_name`, `parser_version`: populated after successful parsing (P1); feed
  `provenance.parser_name`/`parser_version` in the API response
- `parse_error_code`: set alongside `error_code` when the failure originated from parsing
  (P1); internal diagnostic field, not returned by the API

### Clause
- `id`: stable within the review
- `review_id`
- `clause_type`: closed enumeration; values are the canonical set from `DEFENSE_PLAYBOOK_TEMPLATE.md`
  (`confidentiality`, `data_handling`, `subcontracting`, `audit_inspection`,
  `intellectual_property`, `liability_indemnity`, `termination_exit`, `security_incident`,
  `unknown`) as of P2 — P0/P1 used ad hoc strings (`subcontractors`, `liability`,
  `termination`, `security`) in the fixed-result placeholder, corrected in P2 since
  `clause_type` became rule-lookup-load-bearing
- `title`
- `section_reference`
- `page_start`, `page_end`
- `extracted_text`
- `classification_confidence`

### Finding
- `id`
- `review_id`, `clause_id`: `clause_id` is nullable only for missing-clause findings
- `rule_id`
- `finding_type`: `deviation | missing_clause | compliant | needs_review`
- `risk_label`: `Low | Medium | High | Critical`
- `evidence_text`
- `deviation_reason`
- `recommended_action`
- `source`: `rule | model_assisted_rule`
- `needs_review`
- `classification_confidence`: nullable for missing-clause findings
- `title`, `section_reference`, `page_start`, `page_end`: nullable where no source clause exists
- `guidance`: P4, JSON-encoded list of `{id, text, category, source_note, score}` objects
  (stored as `guidance_json`, `Text`, default `"[]"`). Supplemental only — attached by
  `job_runner._attach_guidance` strictly after rule evaluation and never read by
  `rule_engine.py`. Empty when retrieval is degraded or the triggered rule has no authored
  guidance. **Schema-change note:** this column has no migration path in the prototype;
  a SQLite volume created before P4 must be reset (`docker compose down -v`) before the
  updated backend will run against it.

### RuntimeConfiguration
- `provider_type`: `ollama | anthropic | openai | gemini`
- `model_name`
- `base_url`: server-side only where required
- `base_url_display`: masked or omitted API representation
- `has_credential`: boolean returned to UI
- `deployment_mode`: `local | demo`
- `playbook_id`: active canonical playbook identifier
- `synthetic_data_only`: derived deployment-policy boolean returned to the UI; `true` in hosted Demo mode and `false` in local mode
- `updated_at`

Credentials are not stored in this entity or the result database. Hosted Demo mode uses an environment-provided bootstrap credential with an optional write-only, in-memory admin override that clears on restart. The target enterprise deployment uses an approved secret manager.

## Storage Boundaries
- SQLite is the prototype source of truth for review metadata and results.
- Original uploads are temporary and are not stored after the configured retention period.
- Qdrant stores only the static, admin-managed guidance corpus
  (`playbooks/guidance-v1.json`) and its embeddings — never per-review or contract-derived
  data, and never the source of truth for findings. Retrieved guidance for a given review is
  copied into that review's own `Finding.guidance` (SQLite), so deleting a review needs no
  corresponding Qdrant-side cleanup (a correction from the original plan, which anticipated
  per-review vectors — see `WORKFLOW_SPEC.md` stage 9's P4 note).
- Full contract text must not be embedded into logs, metrics, or configuration history.

## Retention Defaults
- Hosted Demo mode: delete original files immediately after processing; delete review records after 24 hours.
- Local development: configurable, default 7 days.
- Target enterprise: policy-controlled and unresolved in the PoC.

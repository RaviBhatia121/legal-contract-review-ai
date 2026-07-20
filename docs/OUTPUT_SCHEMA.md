# Part 2 Structured Output Contract

## Version
Schema version: `1.0-draft`

`provenance.parser_name`/`parser_version` are live values as of P1 (`pypdf+python-docx`
and the installed library versions; see `TECH_STACK_AND_LICENSES.md`), not placeholders.
`document.page_count`/`document.language` are also derived from the real parsed document as
of P1. As of P2, `findings`, `missing_clauses`, and `review_summary` are real —
produced by `backend/app/services/rule_engine.py` evaluating the deterministic playbook
(`playbooks/defense-services-v1.json`) over extracted attributes (see
`DEFENSE_PLAYBOOK_TEMPLATE.md` and `RULE_EVALUATION_SPEC.md`), not the P0 fixed fixture.
`provenance.model_provider`/`model_name` are `"rule-engine"`/`"none"` in the default
deterministic mode, since no model is involved; `source` is `"rule"`.

As of P3, an opt-in model-assisted extraction path exists
(`PART2_CLAUSE_INTELLIGENCE_MODE=model`, only Ollama wired) feeding the same rule-evaluation
core. When active, `provenance.model_provider`/`model_name` reflect the configured Ollama
provider/model, and `source` is `"model_assisted_rule"` on evidence-based findings
(missing-clause findings stay `"rule"` — they have no clause evidence to attribute to a
model). The deterministic path remains the default everywhere and the fallback/test-double.

As of P4, every finding carries a `guidance` array — supplemental, illustrative
decision-support content retrieved from Qdrant after rule evaluation, keyed by that
finding's `rule_id` (`backend/app/services/guidance_retrieval.py`). It is empty when
retrieval is degraded (`provenance.retrieval_mode: "degraded_full_rules"`, e.g. Qdrant/the
embedding model unreachable) or when the triggered rule has no authored guidance yet.
Guidance can never change `rule_id`, `risk_label`, `finding_type`, or any other field on the
same finding — verified live by comparing retrieval-on and retrieval-off runs of the same
document (see `IMPLEMENTATION_PHASE_PLAN.md` P4 Completion Notes).

The API returns structured data only. Explanatory text exists only inside defined fields.

## Completed Review Example

```json
{
  "schema_version": "1.0-draft",
  "review_id": "018f0000-0000-7000-8000-000000000001",
  "document": {
    "name": "example-services-agreement.pdf",
    "sha256": "lowercase-hex-digest",
    "page_count": 10,
    "language": "en"
  },
  "status": "completed",
  "review_summary": {
    "overall_risk": "Critical",
    "clauses_reviewed": 18,
    "findings_total": 2,
    "findings_by_risk": {
      "Critical": 1,
      "High": 1,
      "Medium": 0,
      "Low": 0
    },
    "missing_clause_count": 1,
    "needs_review_count": 0
  },
  "findings": [
    {
      "finding_id": "F-001",
      "finding_type": "deviation",
      "clause_id": "C-004",
      "clause_type": "data_handling",
      "title": "Data Hosting",
      "section_reference": "Section 6.2",
      "page_start": 4,
      "page_end": 4,
      "evidence_text": "The Supplier may process Customer Data using regional public cloud services.",
      "classification_confidence": 0.96,
      "risk_label": "Critical",
      "rule_id": "DATA-001",
      "deviation_reason": "The clause permits processing outside approved client-controlled systems.",
      "recommended_action": "Restrict processing to approved client-controlled environments.",
      "needs_review": false,
      "source": "model_assisted_rule",
      "guidance": [
        {
          "id": "G-DATA-001-1",
          "text": "Sensitive data processed or stored outside approved, client-controlled systems is a high-risk pattern in defense-sector engagements.",
          "category": "negotiation_tip",
          "source_note": "Illustrative negotiation guidance.",
          "score": 0.93
        }
      ]
    }
  ],
  "missing_clauses": [
    {
      "finding_id": "F-007",
      "finding_type": "missing_clause",
      "clause_type": "audit_inspection",
      "risk_label": "High",
      "rule_id": "AUD-001",
      "deviation_reason": "No audit or inspection right was identified.",
      "recommended_action": "Add risk-based audit and evidence-access rights.",
      "needs_review": false,
      "source": "rule",
      "guidance": []
    }
  ],
  "provenance": {
    "deployment_mode": "demo",
    "department": "Legal",
    "pipeline_version": "1.0-draft",
    "playbook_version": "1.0-draft",
    "prompt_version": "1.0-draft",
    "parser_name": "pypdf+python-docx",
    "parser_version": "pypdf=6.x;python-docx=1.x",
    "model_provider": "provider-id",
    "model_name": "model-id",
    "model_revision": "revision-if-available",
    "retrieval_mode": "qdrant",
    "completed_at": "2026-07-18T12:00:00Z"
  }
}
```

## Enumerations
- `status`: `queued | parsing | analyzing | validating | completed | failed`
- `finding_type`: `deviation | missing_clause | compliant | needs_review`
- `risk_label`: `Low | Medium | High | Critical`
- `source`: `rule | model_assisted_rule`
- `deployment_mode`: `local | demo`
- `retrieval_mode`: `qdrant | degraded_full_rules`
- `guidance[].category`: `negotiation_tip | approved_example | playbook_reference`
- `clause_type`: values defined in `DEFENSE_PLAYBOOK_TEMPLATE.md`
- `document.language`: BCP 47 language code or `unknown`

## In-Progress Review Shape

```json
{
  "schema_version": "1.0-draft",
  "review_id": "018f0000-0000-7000-8000-000000000001",
  "status": "analyzing",
  "current_stage": "checking_playbook",
  "created_at": "2026-07-18T11:58:00Z",
  "started_at": "2026-07-18T11:58:01Z"
}
```

`current_stage` is a display-safe substage and does not add a persisted review status.

Allowed active `current_stage` values:
- `queued`
- `parsing_document`
- `checking_applicability`
- `classifying_clauses`
- `checking_playbook`
- `extracting_attributes`
- `evaluating_rules`
- `validating_result`

Status-to-stage mapping:

| Persisted `status` | Allowed `current_stage` |
|---|---|
| `queued` | `queued` |
| `parsing` | `parsing_document` |
| `analyzing` | `checking_applicability`, `classifying_clauses`, `checking_playbook`, `extracting_attributes`, `evaluating_rules` |
| `validating` | `validating_result` |
| `completed` | `null` |
| `failed` | `null` |

## Validation Rules
- A completed review has non-empty provenance and a review summary.
- A failed review has an `error` object and no fabricated successful summary.
- `NO_REVIEWABLE_TEXT` and `DOCUMENT_NOT_APPLICABLE` are failed outcomes and never contain fabricated missing-clause findings.
- `evidence_text` is required for deviation, compliant, and needs-review clause findings.
- Missing-clause findings do not contain invented evidence.
- Every finding has a valid playbook `rule_id`.
- Summary counts must equal the returned findings.
- `findings_total` and `findings_by_risk` include both `findings` and `missing_clauses` arrays.
- Overall risk must equal the highest finding severity.
- API keys, prompts, chain-of-thought, and hidden model reasoning are never fields.
- `guidance` is supplemental only: it never determines `rule_id`, `risk_label`,
  `finding_type`, `deviation_reason`, or `recommended_action`, and an empty `guidance` array
  is a valid, expected value (degraded retrieval or no authored guidance for that rule).

## Failed Review Shape

```json
{
  "schema_version": "1.0-draft",
  "review_id": "018f0000-0000-7000-8000-000000000001",
  "status": "failed",
  "error": {
    "code": "MODEL_OUTPUT_INVALID",
    "message": "The review could not produce a valid structured result.",
    "retryable": true
  }
}
```

# Part 2 Rule Evaluation Specification

Implemented as of P2 in `backend/app/services/rule_engine.py`, evaluated over
attributes produced by `backend/app/services/attribute_extraction.py`. In P2
that extraction is deterministic, fixture-oriented pattern matching, not the
"model-assisted" extraction this spec was originally written for — see the
Purpose line below and the P2 boundary note under Confidence Handling.
Real, general model-assisted extraction is P3 scope
(`MODEL_AND_PIPELINE_CONTRACT.md`); this spec's predicates themselves are
already general (they operate on the normalized attribute contract, not on
how the attributes were produced) and required no change for P2. See
`DEFENSE_PLAYBOOK_TEMPLATE.md`'s Confidence Handling section for how P2's
pattern-match-derived confidence feeds this spec's confidence bands.

## Purpose
Convert model-assisted clause extraction into deterministic predicates. Unknown values never default to compliant.

## Normalized Values
Every attribute is returned as an enum, boolean, number, or `unknown`, with one or more evidence spans.

| Clause Type | Normalized Attributes |
|---|---|
| confidentiality | `present`, `disclosure_scope: restricted, affiliates, third_parties, public, or unknown`, `need_to_know_required`, `equivalent_obligations_required` |
| data_handling | `present`, `external_cloud_allowed`, `approved_systems_only`, `cross_border_allowed`, `prior_approval_required`, `location_defined`, `retention_defined`, `return_defined`, `verified_deletion_defined` |
| subcontracting | `present`, `prior_approval_required`, `sensitive_access_allowed`, `security_flow_down`, `confidentiality_flow_down`, `audit_flow_down`, `data_flow_down` |
| audit_inspection | `present`, `customer_audit_right`, `independent_evidence_allowed`, `vendor_summary_only` |
| intellectual_property | `present`, `bespoke_owner: customer, vendor, shared, or unknown`, `background_ip_retained_by_vendor`, `customer_license_sufficient` |
| liability_indemnity | `present`, `cap_exists`, `cap_basis`, `confidentiality_carveout`, `security_data_carveout`, `ip_carveout`, `fraud_wilful_misconduct_carveout`, `supplier_ip_indemnity` |
| termination_exit | `present`, `material_breach_termination`, `security_event_termination`, `data_return`, `verified_deletion`, `transition_assistance` |
| security_incident | `present`, `access_control`, `encryption`, `logging`, `vulnerability_management`, `incident_notice_hours` |

## Predicate Rules
- `CONF-001`: `disclosure_scope == public`.
- `CONF-002`: `disclosure_scope in [affiliates, third_parties]` and either `need_to_know_required != true` or `equivalent_obligations_required != true`.
- `CONF-003`: `present == false`.
- `DATA-001`: `external_cloud_allowed == true` or `approved_systems_only == false`.
- `DATA-002`: any of `location_defined`, `retention_defined`, `return_defined`, `verified_deletion_defined` is `false` or `unknown`.
- `DATA-003`: `cross_border_allowed == true` and `prior_approval_required != true`.
- `DATA-004`: `present == false`.
- `SUB-001`: `sensitive_access_allowed == true` and `prior_approval_required != true`.
- `SUB-002`: any required flow-down attribute is `false` or `unknown`.
- `SUB-003`: `present == false`.
- `AUD-001`: `present == false` or `customer_audit_right != true`.
- `AUD-002`: `vendor_summary_only == true` and `independent_evidence_allowed != true`.
- `IP-001`: `bespoke_owner == vendor` and `customer_license_sufficient != true`.
- `IP-002`: `bespoke_owner in [customer, shared]`, `background_ip_retained_by_vendor == true`, and `customer_license_sufficient == true`.
- `IP-003`: `present == false`.
- `LIAB-001`: `cap_exists == true` and any required carve-out is `false` or `unknown`.
- `LIAB-002`: `supplier_ip_indemnity != true`.
- `LIAB-003`: `present == false`.
- `TERM-001`: both `material_breach_termination != true` and `security_event_termination != true`.
- `TERM-002`: any of `data_return`, `verified_deletion`, `transition_assistance` is `false` or `unknown`.
- `TERM-003`: `present == false`.
- `TERM-004`: `material_breach_termination == true`, `security_event_termination == true`, `data_return == true`, `verified_deletion == true`, and `transition_assistance == true`.
- `SEC-001`: any of `access_control`, `encryption`, `logging`, `vulnerability_management` is `false` or `unknown`.
- `SEC-002`: `incident_notice_hours == unknown` or `incident_notice_hours > 24`.
- `SEC-003`: all four minimum security controls are `true` and `incident_notice_hours <= 24`.
- `SEC-004`: `present == false`.
- `REV-001`: `classification_confidence < 0.60`.

## Presence and Unknown Rules
- `present` is application-computed from classified evidence, not model opinion alone.
- An absent required clause triggers the exact missing rule mapped in `DEFENSE_PLAYBOOK_TEMPLATE.md` and skips all other predicates for that clause type.
- `unknown` is non-compliant where the rule requires an explicit contractual protection.
- A predicate may emit at most one finding per distinct supporting clause.
- `REV-001` is evaluated before presence and clause-type predicates.
- For every relevant candidate below `0.60`, emit `REV-001`. After all candidates are evaluated, emit the mapped missing-clause rule as well when no candidate at or above `0.60` establishes the required clause type. This behavior is mandatory, not optional, and both findings contribute to summary counts.

## Evidence Rule
Every normalized non-unknown value must cite verbatim text. Values without evidence are changed to `unknown` before rule evaluation.

## Finding-Type Mapping
- A mapped missing rule triggered by `present == false` emits `missing_clause`.
- `IP-002`, `TERM-004`, and `SEC-003` emit `compliant`.
- `REV-001` emits `needs_review`.
- Every other triggered rule emits `deviation`.
- `AUD-001` emits `missing_clause` when the audit clause is absent and `deviation` when a clause exists but grants no customer audit right.

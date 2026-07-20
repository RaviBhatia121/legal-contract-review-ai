# Defense-Services Contract Review Playbook

This document is the source of truth for the playbook. It is transcribed
verbatim into the machine-readable `playbooks/defense-services-v1.json`
(loaded by `backend/app/playbook/loader.py`) as of P2 — that file only
parses and validates the data below, it does not encode rule logic itself.
Rule predicates live in `backend/app/services/rule_engine.py`, implementing
`RULE_EVALUATION_SPEC.md` exactly.

## Version and Authority
- Playbook ID: `defense-services-v1`
- Playbook version: `1.0-draft`
- Status: prototype specification for review
- Intended documents: vendor MSA, services agreement, procurement agreement, SOW, support/data addendum
- Jurisdiction: organization policy baseline, not a statement of Indonesian law

This playbook is illustrative decision-support logic. Production use requires validation by the client's Legal, Security, Procurement, and Compliance owners.

## Clause-Type Enumeration
- `confidentiality`
- `data_handling`
- `subcontracting`
- `audit_inspection`
- `intellectual_property`
- `liability_indemnity`
- `termination_exit`
- `security_incident`
- `unknown`

## Rule Table

| Rule ID | Area | Trigger | Severity | Recommended Action |
|---|---|---|---|---|
| CONF-001 | Confidentiality | Public or unrestricted disclosure of protected information is permitted | Critical | Prohibit disclosure except for narrowly defined legal obligations |
| CONF-002 | Confidentiality | Affiliate, adviser, or third-party disclosure lacks need-to-know and equivalent obligations | High | Require need-to-know access and written flow-down obligations |
| CONF-003 | Confidentiality | Confidentiality clause is absent | High | Add approved mutual confidentiality clause |
| DATA-001 | Data handling | Sensitive data may be processed or stored in external/public cloud or outside approved systems | Critical | Restrict processing to approved client-controlled environments |
| DATA-002 | Data handling | Data location, retention, return, or deletion is not defined | High | Add location, retention, return, and verified deletion terms |
| DATA-003 | Data handling | Cross-border transfer is permitted without prior written approval | Critical | Require prior approval and approved transfer controls |
| DATA-004 | Data handling | Data-handling clause is absent | High | Add approved data location, use, retention, return, and deletion terms |
| SUB-001 | Subcontracting | Subcontractors may access services/data without prior written approval | High | Require approval before appointment or access |
| SUB-002 | Subcontracting | Security, confidentiality, audit, and data obligations do not flow down | High | Add equivalent written flow-down obligations |
| SUB-003 | Subcontracting | Subcontracting clause is absent | High | Add approval and flow-down requirements for subcontractors |
| AUD-001 | Audit | Customer has no audit or inspection right over relevant controls | High | Add risk-based audit and evidence-access rights |
| AUD-002 | Audit | Audit right is restricted to vendor-selected summaries only | Medium | Permit independent evidence or assessment subject to safeguards |
| IP-001 | Intellectual property | Vendor owns bespoke paid deliverables without sufficient customer rights | High | Assign bespoke deliverables or grant perpetual enterprise rights |
| IP-002 | Intellectual property | Vendor background IP is retained while customer receives sufficient use rights | Low | Accept if license is perpetual, adequate, and documented |
| IP-003 | Intellectual property | Intellectual-property clause is absent | High | Add ownership and license terms for deliverables and background IP |
| LIAB-001 | Liability | Liability cap includes confidentiality, data/security breach, IP infringement, fraud, or wilful misconduct without carve-outs | High | Add appropriate carve-outs or higher super-cap |
| LIAB-002 | Liability | Supplier indemnity for third-party IP infringement is absent | High | Add defense and indemnity obligation |
| LIAB-003 | Liability | Liability and indemnity clause is absent | High | Add approved liability, carve-out, and indemnity terms |
| TERM-001 | Termination | Customer lacks termination for material breach or security event | High | Add termination rights and cure rules where appropriate |
| TERM-002 | Termination | Data return/deletion and transition assistance are absent | High | Add exit, return, verified deletion, and transition duties |
| TERM-003 | Termination | Termination and exit clause is absent | High | Add termination, data disposition, and transition obligations |
| TERM-004 | Termination | Material/security termination, data return, verified deletion, and transition assistance are all present | Low | Accept subject to Legal validation |
| SEC-001 | Security | Minimum access control, encryption, logging, or vulnerability-management obligations are absent | High | Add the approved security schedule |
| SEC-002 | Security | Security incident notification deadline is absent or exceeds 24 hours from awareness | High | Require initial notice within 24 hours and continuing updates |
| SEC-003 | Security | Security controls and incident handling are adequately stated | Low | Accept subject to technical validation |
| SEC-004 | Security | Security and incident clause is absent | High | Add the approved security and incident-response schedule |
| REV-001 | Review quality | Clause classification confidence is below `0.60` | Medium | Route the evidence for human review and do not treat the required clause as present |

## Required Clause Rules
For a services agreement that processes or accesses sensitive information, these clause types are required:
- confidentiality
- data_handling
- subcontracting
- audit_inspection
- intellectual_property
- liability_indemnity
- termination_exit
- security_incident

Use this exact missing-clause mapping:

| Clause Type | Missing Rule |
|---|---|
| confidentiality | `CONF-003` |
| data_handling | `DATA-004` |
| subcontracting | `SUB-003` |
| audit_inspection | `AUD-001` |
| intellectual_property | `IP-003` |
| liability_indemnity | `LIAB-003` |
| termination_exit | `TERM-003` |
| security_incident | `SEC-004` |

Do not create both a missing and a deviation finding for the same absent clause.

## Evaluation Order
1. Determine document type and applicability.
   - If parsed text is empty or unusable, fail with `NO_REVIEWABLE_TEXT`.
   - If the document is outside the intended-document scope above, fail with `DOCUMENT_NOT_APPLICABLE`.
   - In either case, do not run clause rules or fabricate missing-clause findings.
2. Map extracted clauses to the closed clause-type enumeration.
3. Mark required clause types as present only when supported by verbatim evidence.
4. Normalize clause attributes.
5. Evaluate rules in ascending rule-ID order.
6. Emit all distinct triggered rules; deduplicate identical rule/evidence pairs.
7. Aggregate the review risk using the fixed rule below.

## Overall-Risk Aggregation
- `Critical` if one or more Critical findings exist.
- Otherwise `High` if one or more High findings exist.
- Otherwise `Medium` if one or more Medium findings exist.
- Otherwise `Low`.

Do not average severities. A model cannot lower a rule-defined severity.

## Confidence Handling
- `>= 0.80`: evaluate normally.
- `0.60-0.79`: evaluate normally and set `needs_review: true` on resulting findings.
- `< 0.60`: classify as `unknown`, preserve evidence, emit `REV-001`, and do not treat the required clause type as present. After all candidates are evaluated, also emit the mapped missing-clause rule when no accepted clause at or above `0.60` establishes presence. Both findings are included in summary counts.

**P2 confidence source:** there is no model in P2, so confidence is a
deterministic pattern-match-strength heuristic
(`backend/app/services/attribute_extraction.py`): a known trigger phrase
matched → high confidence (0.95); a recognized clause heading whose body
matched no known trigger phrase → low confidence (0.45, below the `REV-001`
floor). This correctly exercises the confidence-banding logic above, but it
is not a real classifier probability. Real, general model confidence is P3
scope.

`AUD-001` is deliberately dual-purpose: it is a `missing_clause` when no accepted audit clause is present and a `deviation` when an accepted clause exists but grants no customer audit right.

## Display Policy
- Critical, High, Medium, and needs-review findings are visible by default.
- Low/compliant findings are collapsed by default but remain available to demonstrate review coverage.

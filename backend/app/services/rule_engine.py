"""Deterministic rule engine (P2, extraction-source-agnostic since P3).

Implements RULE_EVALUATION_SPEC.md's predicates and confidence handling and
DEFENSE_PLAYBOOK_TEMPLATE.md's missing-clause mapping and risk aggregation.

`evaluate_clauses` is the reusable core: it takes a list of `ClauseInput` —
one per detected clause, with normalized attributes, confidence, and
evidence — and applies the playbook. It has no idea whether those
`ClauseInput`s came from P2's deterministic fixture-oriented segmentation
(`segmentation.py`/`attribute_extraction.py`, see `evaluate_document` below)
or P3's model-assisted pipeline (`clause_intelligence.py`). The model can
never set a rule_id, severity, or recommended_action — those always come
from the playbook via `_make_finding`.
"""

from dataclasses import dataclass
from typing import Any, Callable

from app.playbook.loader import Playbook
from app.services.attribute_extraction import extract_attributes
from app.services.parsing import ParsedDocument
from app.services.segmentation import ClauseSegment, segment_document

_LOW_CONFIDENCE_FLOOR = 0.60
_NEEDS_REVIEW_CEILING = 0.80

_COMPLIANT_RULES = {"IP-002", "TERM-004", "SEC-003"}
_SEVERITY_ORDER = {"Critical": 3, "High": 2, "Medium": 1, "Low": 0}


@dataclass(frozen=True)
class ClauseInput:
    """Source-agnostic input to `evaluate_clauses` — one per detected clause."""

    clause_type: str
    title: str
    section_reference: str
    page_start: int
    page_end: int
    evidence_text: str
    confidence: float
    attributes: dict[str, Any]


@dataclass(frozen=True)
class ClauseRecord:
    key: str
    clause_type: str
    title: str
    section_reference: str
    page_start: int
    page_end: int
    extracted_text: str
    classification_confidence: float


@dataclass(frozen=True)
class FindingRecord:
    finding_type: str
    clause_key: str | None
    clause_type: str
    title: str | None
    section_reference: str | None
    page_start: int | None
    page_end: int | None
    evidence_text: str | None
    classification_confidence: float | None
    risk_label: str
    rule_id: str
    deviation_reason: str
    recommended_action: str
    needs_review: bool
    source: str


def _is_true(v: Any) -> bool:
    return v is True


def _is_false_or_unknown(v: Any) -> bool:
    return v is False or v == "unknown"


def _any_false_or_unknown(attrs: dict[str, Any], keys: list[str]) -> bool:
    return any(_is_false_or_unknown(attrs.get(k, "unknown")) for k in keys)


# Predicate functions take the normalized attribute dict and return whether
# the rule is triggered. Keyed by rule_id; grouped by clause_type below only
# for evaluation ordering. AUD-001 here is the "present but insufficient"
# (deviation) branch only — the "absent" (missing_clause) branch is handled
# by the generic missing-clause pass in evaluate_clauses.
_PREDICATES: dict[str, Callable[[dict[str, Any]], bool]] = {
    "CONF-001": lambda a: a.get("disclosure_scope") == "public",
    "CONF-002": lambda a: a.get("disclosure_scope") in ("affiliates", "third_parties")
    and (not _is_true(a.get("need_to_know_required")) or not _is_true(a.get("equivalent_obligations_required"))),
    "DATA-001": lambda a: _is_true(a.get("external_cloud_allowed")) or a.get("approved_systems_only") is False,
    "DATA-002": lambda a: _any_false_or_unknown(
        a, ["location_defined", "retention_defined", "return_defined", "verified_deletion_defined"]
    ),
    "DATA-003": lambda a: _is_true(a.get("cross_border_allowed")) and not _is_true(a.get("prior_approval_required")),
    "SUB-001": lambda a: _is_true(a.get("sensitive_access_allowed")) and not _is_true(a.get("prior_approval_required")),
    "SUB-002": lambda a: _any_false_or_unknown(
        a, ["security_flow_down", "confidentiality_flow_down", "audit_flow_down", "data_flow_down"]
    ),
    "AUD-001": lambda a: not _is_true(a.get("customer_audit_right")),
    "AUD-002": lambda a: _is_true(a.get("vendor_summary_only")) and not _is_true(a.get("independent_evidence_allowed")),
    "IP-001": lambda a: a.get("bespoke_owner") == "vendor" and not _is_true(a.get("customer_license_sufficient")),
    "IP-002": lambda a: a.get("bespoke_owner") in ("customer", "shared")
    and _is_true(a.get("background_ip_retained_by_vendor"))
    and _is_true(a.get("customer_license_sufficient")),
    "LIAB-001": lambda a: _is_true(a.get("cap_exists"))
    and _any_false_or_unknown(
        a, ["confidentiality_carveout", "security_data_carveout", "ip_carveout", "fraud_wilful_misconduct_carveout"]
    ),
    "LIAB-002": lambda a: not _is_true(a.get("supplier_ip_indemnity")),
    "TERM-001": lambda a: not _is_true(a.get("material_breach_termination"))
    and not _is_true(a.get("security_event_termination")),
    "TERM-002": lambda a: _any_false_or_unknown(a, ["data_return", "verified_deletion", "transition_assistance"]),
    "TERM-004": lambda a: all(
        _is_true(a.get(k))
        for k in [
            "material_breach_termination",
            "security_event_termination",
            "data_return",
            "verified_deletion",
            "transition_assistance",
        ]
    ),
    "SEC-001": lambda a: _any_false_or_unknown(
        a, ["access_control", "encryption", "logging", "vulnerability_management"]
    ),
    "SEC-002": lambda a: a.get("incident_notice_hours") == "unknown" or (
        isinstance(a.get("incident_notice_hours"), int) and a["incident_notice_hours"] > 24
    ),
    "SEC-003": lambda a: all(_is_true(a.get(k)) for k in ["access_control", "encryption", "logging", "vulnerability_management"])
    and isinstance(a.get("incident_notice_hours"), int)
    and a["incident_notice_hours"] <= 24,
}

# Evaluated in ascending rule-ID order per clause type (RULE_EVALUATION_SPEC.md).
_RULES_BY_CLAUSE_TYPE: dict[str, list[str]] = {
    "confidentiality": ["CONF-001", "CONF-002"],
    "data_handling": ["DATA-001", "DATA-002", "DATA-003"],
    "subcontracting": ["SUB-001", "SUB-002"],
    "audit_inspection": ["AUD-001", "AUD-002"],
    "intellectual_property": ["IP-001", "IP-002"],
    "liability_indemnity": ["LIAB-001", "LIAB-002"],
    "termination_exit": ["TERM-001", "TERM-002", "TERM-004"],
    "security_incident": ["SEC-001", "SEC-002", "SEC-003"],
}


def _finding_type_for(rule_id: str) -> str:
    if rule_id in _COMPLIANT_RULES:
        return "compliant"
    return "deviation"


def _make_finding(
    playbook: Playbook,
    rule_id: str,
    finding_type: str,
    clause_key: str | None,
    clause_type: str,
    needs_review: bool,
    title: str | None = None,
    section_reference: str | None = None,
    page_start: int | None = None,
    page_end: int | None = None,
    evidence_text: str | None = None,
    confidence: float | None = None,
    source: str = "rule",
) -> FindingRecord:
    rule = playbook.rule_by_id(rule_id)
    is_missing = finding_type == "missing_clause"
    return FindingRecord(
        finding_type=finding_type,
        clause_key=clause_key,
        clause_type=clause_type,
        title=None if is_missing else title,
        section_reference=None if is_missing else section_reference,
        page_start=None if is_missing else page_start,
        page_end=None if is_missing else page_end,
        evidence_text=None if is_missing else evidence_text,
        classification_confidence=None if is_missing else confidence,
        risk_label=rule.severity,
        rule_id=rule.rule_id,
        deviation_reason=rule.trigger,
        recommended_action=rule.recommended_action,
        needs_review=needs_review,
        # Missing-clause findings have no clause evidence backing them — pure
        # playbook logic — so they always stay "rule" regardless of how
        # present clauses were extracted, per OUTPUT_SCHEMA.md's example
        # convention (missing_clause -> "rule", evidence-based -> caller's source).
        source="rule" if is_missing else source,
    )


def evaluate_clauses(
    clause_inputs: list[ClauseInput], playbook: Playbook, source: str = "rule"
) -> tuple[list[ClauseRecord], list[FindingRecord], str]:
    """Source-agnostic core: apply the playbook to a list of already-extracted
    clauses. Used by both the P2 deterministic path (`evaluate_document`) and
    the P3 model-assisted path (`clause_intelligence.py`)."""
    clauses: list[ClauseRecord] = []
    findings: list[FindingRecord] = []
    present_clause_types: set[str] = set()

    by_type: dict[str, list[ClauseInput]] = {}
    for ci in clause_inputs:
        by_type.setdefault(ci.clause_type, []).append(ci)

    for clause_type, inputs in by_type.items():
        if clause_type not in _RULES_BY_CLAUSE_TYPE:
            continue  # unmapped clause_type (e.g. "unknown"); nothing to evaluate

        for idx, ci in enumerate(inputs):
            clause_key = f"{clause_type}:{idx}"
            clauses.append(
                ClauseRecord(
                    key=clause_key,
                    clause_type=clause_type,
                    title=ci.title,
                    section_reference=ci.section_reference,
                    page_start=ci.page_start,
                    page_end=ci.page_end,
                    extracted_text=ci.evidence_text,
                    classification_confidence=ci.confidence,
                )
            )

            common_kwargs = dict(
                title=ci.title,
                section_reference=ci.section_reference,
                page_start=ci.page_start,
                page_end=ci.page_end,
                evidence_text=ci.evidence_text,
                confidence=ci.confidence,
                source=source,
            )

            if ci.confidence < _LOW_CONFIDENCE_FLOOR:
                findings.append(
                    _make_finding(
                        playbook, "REV-001", "needs_review", clause_key, clause_type, True, **common_kwargs
                    )
                )
                continue  # not treated as present; missing-clause rule may still fire below

            present_clause_types.add(clause_type)
            needs_review = ci.confidence < _NEEDS_REVIEW_CEILING

            for rule_id in _RULES_BY_CLAUSE_TYPE[clause_type]:
                if rule_id == "AUD-001":
                    continue  # handled via the missing-clause pass below when absent; deviation branch only if present
                if _PREDICATES[rule_id](ci.attributes):
                    findings.append(
                        _make_finding(
                            playbook,
                            rule_id,
                            _finding_type_for(rule_id),
                            clause_key,
                            clause_type,
                            needs_review,
                            **common_kwargs,
                        )
                    )

            if clause_type == "audit_inspection" and _PREDICATES["AUD-001"](ci.attributes):
                findings.append(
                    _make_finding(
                        playbook, "AUD-001", "deviation", clause_key, clause_type, needs_review, **common_kwargs
                    )
                )

    # Missing-clause pass: any required clause type with no accepted (>= 0.60
    # confidence) input gets the mapped missing-clause rule. AUD-001 is
    # dual-purpose (see module docstring / RULE_EVALUATION_SPEC.md) — when
    # audit_inspection is present at all (even below 0.60), a REV-001 was
    # already emitted for it above, and the missing-clause AUD-001 below
    # still fires since it wasn't added to present_clause_types in that case.
    for clause_type in playbook.required_clause_types:
        if clause_type in present_clause_types:
            continue
        rule_id = playbook.missing_clause_rule_by_type[clause_type]
        findings.append(_make_finding(playbook, rule_id, "missing_clause", None, clause_type, False))

    findings.sort(key=lambda f: f.rule_id)
    overall_risk = aggregate_risk(findings)
    return clauses, findings, overall_risk


def build_deterministic_clause_inputs(parsed: ParsedDocument) -> list[ClauseInput]:
    """P2 deterministic path: fixture-oriented segmentation + extraction,
    producing the same source-agnostic `ClauseInput` the P3 model-assisted
    path produces. Kept as the default/fallback/test-double path; see
    IMPLEMENTATION_PHASE_PLAN.md P3 notes."""
    segments = segment_document(parsed.text, parsed.page_boundaries)

    segments_by_type: dict[str, list[ClauseSegment]] = {}
    for seg in segments:
        segments_by_type.setdefault(seg.clause_type, []).append(seg)

    clause_inputs: list[ClauseInput] = []
    for clause_type, segs in segments_by_type.items():
        for seg in segs:
            extraction = extract_attributes(seg)
            clause_inputs.append(
                ClauseInput(
                    clause_type=clause_type,
                    title=seg.heading,
                    section_reference=extraction.section_reference,
                    page_start=seg.page_start,
                    page_end=seg.page_end,
                    evidence_text=extraction.evidence_text,
                    confidence=extraction.confidence,
                    attributes=extraction.attributes,
                )
            )
    return clause_inputs


def evaluate_document(parsed: ParsedDocument, playbook: Playbook) -> tuple[list[ClauseRecord], list[FindingRecord], str]:
    """P2 deterministic path, end to end: build clause inputs, then evaluate."""
    clause_inputs = build_deterministic_clause_inputs(parsed)
    return evaluate_clauses(clause_inputs, playbook)


def aggregate_risk(findings: list[FindingRecord]) -> str:
    if not findings:
        return "Low"
    highest = max(findings, key=lambda f: _SEVERITY_ORDER[f.risk_label])
    return highest.risk_label

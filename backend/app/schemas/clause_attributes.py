"""Per-clause-type normalized attribute specs, mirroring RULE_EVALUATION_SPEC.md
exactly (same attribute names P2's `attribute_extraction.py` already uses, so
`rule_engine.py`'s predicates work identically regardless of extraction
source).

Used to normalize raw P-02 model output (a flat list of attribute/value
pairs) into the typed dict `rule_engine._PREDICATES` expects. Any attribute
missing, of the wrong kind, or not in the enum is coerced to `"unknown"` —
never silently defaulted to compliant, per RULE_EVALUATION_SPEC.md's Evidence
Rule.
"""

from typing import Any

# kind is one of: "bool", "int", "str", or "enum:<comma-separated-values>"
ATTRIBUTE_SPECS: dict[str, dict[str, str]] = {
    "confidentiality": {
        "present": "bool",
        "disclosure_scope": "enum:restricted,affiliates,third_parties,public",
        "need_to_know_required": "bool",
        "equivalent_obligations_required": "bool",
    },
    "data_handling": {
        "present": "bool",
        "external_cloud_allowed": "bool",
        "approved_systems_only": "bool",
        "cross_border_allowed": "bool",
        "prior_approval_required": "bool",
        "location_defined": "bool",
        "retention_defined": "bool",
        "return_defined": "bool",
        "verified_deletion_defined": "bool",
    },
    "subcontracting": {
        "present": "bool",
        "prior_approval_required": "bool",
        "sensitive_access_allowed": "bool",
        "security_flow_down": "bool",
        "confidentiality_flow_down": "bool",
        "audit_flow_down": "bool",
        "data_flow_down": "bool",
    },
    "audit_inspection": {
        "present": "bool",
        "customer_audit_right": "bool",
        "independent_evidence_allowed": "bool",
        "vendor_summary_only": "bool",
    },
    "intellectual_property": {
        "present": "bool",
        "bespoke_owner": "enum:customer,vendor,shared",
        "background_ip_retained_by_vendor": "bool",
        "customer_license_sufficient": "bool",
    },
    "liability_indemnity": {
        "present": "bool",
        "cap_exists": "bool",
        "cap_basis": "str",
        "confidentiality_carveout": "bool",
        "security_data_carveout": "bool",
        "ip_carveout": "bool",
        "fraud_wilful_misconduct_carveout": "bool",
        "supplier_ip_indemnity": "bool",
    },
    "termination_exit": {
        "present": "bool",
        "material_breach_termination": "bool",
        "security_event_termination": "bool",
        "data_return": "bool",
        "verified_deletion": "bool",
        "transition_assistance": "bool",
    },
    "security_incident": {
        "present": "bool",
        "access_control": "bool",
        "encryption": "bool",
        "logging": "bool",
        "vulnerability_management": "bool",
        "incident_notice_hours": "int",
    },
}


def _coerce(value: Any, kind: str) -> Any:
    if value is None:
        return "unknown"
    if kind == "bool":
        return value if isinstance(value, bool) else "unknown"
    if kind == "int":
        if isinstance(value, bool):
            return "unknown"
        if isinstance(value, int):
            return value
        return "unknown"
    if kind == "str":
        return value if isinstance(value, str) and value != "unknown" else (value or "unknown")
    if kind.startswith("enum:"):
        allowed = set(kind.removeprefix("enum:").split(","))
        return value if value in allowed else "unknown"
    return "unknown"


def normalize_attributes(clause_type: str, raw: dict[str, Any]) -> dict[str, Any]:
    """Return the normalized attribute dict for a clause type, coercing
    anything missing or malformed to "unknown" rather than trusting the
    model's shape."""
    spec = ATTRIBUTE_SPECS.get(clause_type, {})
    return {name: _coerce(raw.get(name), kind) for name, kind in spec.items()}


def attribute_names_for(clause_type: str) -> list[str]:
    return list(ATTRIBUTE_SPECS.get(clause_type, {}).keys())

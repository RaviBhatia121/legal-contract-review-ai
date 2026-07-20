from app.playbook.loader import load_playbook


def test_loads_all_rules():
    pb = load_playbook()
    assert pb.playbook_id == "defense-services-v1"
    assert pb.playbook_version == "1.0-draft"
    assert len(pb.rules) == 27


def test_required_clause_types():
    pb = load_playbook()
    assert pb.required_clause_types == (
        "confidentiality",
        "data_handling",
        "subcontracting",
        "audit_inspection",
        "intellectual_property",
        "liability_indemnity",
        "termination_exit",
        "security_incident",
    )


def test_missing_clause_rule_mapping():
    pb = load_playbook()
    assert pb.missing_clause_rule_by_type == {
        "confidentiality": "CONF-003",
        "data_handling": "DATA-004",
        "subcontracting": "SUB-003",
        "audit_inspection": "AUD-001",
        "intellectual_property": "IP-003",
        "liability_indemnity": "LIAB-003",
        "termination_exit": "TERM-003",
        "security_incident": "SEC-004",
    }


def test_rule_by_id():
    pb = load_playbook()
    rule = pb.rule_by_id("DATA-001")
    assert rule.severity == "Critical"
    assert rule.clause_type == "data_handling"


def test_rules_for_clause_type():
    pb = load_playbook()
    conf_rules = pb.rules_for_clause_type("confidentiality")
    assert {r.rule_id for r in conf_rules} == {"CONF-001", "CONF-002", "CONF-003"}


def test_cached_instance_is_reused():
    assert load_playbook() is load_playbook()

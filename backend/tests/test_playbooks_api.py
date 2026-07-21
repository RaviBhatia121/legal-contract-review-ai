import pytest

pytestmark = pytest.mark.asyncio


async def test_active_playbook_returns_read_only_summary(client):
    resp = await client.get("/api/v1/playbooks/active")
    assert resp.status_code == 200
    body = resp.json()

    assert body["playbook_id"] == "defense-services-v1"
    assert body["playbook_version"] == "1.0-draft"
    assert body["editable"] is False
    assert "CRUD requires versioning" in body["edit_policy"]
    assert len(body["rules"]) == 27
    assert len(body["clause_families"]) == 8
    assert len(body["required_clause_types"]) == 8


async def test_active_playbook_marks_required_and_missing_clause_rules(client):
    resp = await client.get("/api/v1/playbooks/active")
    assert resp.status_code == 200
    body = resp.json()

    families = {item["clause_type"]: item for item in body["clause_families"]}
    assert families["audit_inspection"] == {
        "clause_type": "audit_inspection",
        "required": True,
        "missing_clause_rule_id": "AUD-001",
        "rule_count": 2,
    }

    missing_rule_ids = {rule["rule_id"] for rule in body["rules"] if rule["missing_clause_rule"]}
    assert missing_rule_ids == {
        "CONF-003",
        "DATA-004",
        "SUB-003",
        "AUD-001",
        "IP-003",
        "LIAB-003",
        "TERM-003",
        "SEC-004",
    }


async def test_active_playbook_does_not_expose_loader_or_file_internals(client):
    resp = await client.get("/api/v1/playbooks/active")
    assert resp.status_code == 200
    body = resp.json()
    serialized = str(body)

    assert "playbook_dir" not in serialized
    assert "defense-services-v1.json" not in serialized
    assert "/app/playbooks" not in serialized

import asyncio
import json
import os

import pytest

from app.core.config import get_settings

pytestmark = pytest.mark.asyncio

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "fixtures")


def _fixture_bytes(name: str) -> bytes:
    with open(os.path.join(FIXTURES_DIR, name), "rb") as f:
        return f.read()


async def _create_review(client, filename="sentinel-support-agreement.pdf", content_type="application/pdf"):
    content = _fixture_bytes(filename)
    files = {"file": (filename, content, content_type)}
    resp = await client.post("/api/v1/reviews", files=files)
    assert resp.status_code == 202
    return resp.json()


async def _wait_for_completion(client, review_id, timeout_s: float = 5.0):
    elapsed = 0.0
    while elapsed < timeout_s:
        resp = await client.get(f"/api/v1/reviews/{review_id}")
        assert resp.status_code == 200
        body = resp.json()
        if body["status"] in ("completed", "failed"):
            return body
        await asyncio.sleep(0.1)
        elapsed += 0.1
    raise AssertionError("review did not complete in time")


async def test_upload_rejects_unsupported_file_type(client):
    files = {"file": ("notes.txt", b"hello", "text/plain")}
    resp = await client.post("/api/v1/reviews", files=files)
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "UNSUPPORTED_FILE_TYPE"
    assert "request_id" in body["error"]


async def test_upload_rejects_oversized_file(client):
    big_content = b"%PDF-1.4\n" + (b"0" * (15 * 1024 * 1024 + 1))
    files = {"file": ("big.pdf", big_content, "application/pdf")}
    resp = await client.post("/api/v1/reviews", files=files)
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "FILE_TOO_LARGE"


async def test_get_missing_review_returns_404(client):
    resp = await client.get("/api/v1/reviews/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "REVIEW_NOT_FOUND"


async def test_golden_path_upload_to_findings(client):
    created = await _create_review(client)
    assert created["status"] == "queued"
    review_id = created["review_id"]
    assert created["status_url"] == f"/api/v1/reviews/{review_id}"

    result = await _wait_for_completion(client, review_id)

    assert result["schema_version"] == "1.0-draft"
    assert result["status"] == "completed"
    assert result["document"]["name"] == "sentinel-support-agreement.pdf"
    assert len(result["document"]["sha256"]) == 64
    # Real parsing (P1): page count/language come from the actual fixture, not a fixed constant.
    assert result["document"]["page_count"] == 8
    assert result["document"]["language"] == "en"

    summary = result["review_summary"]
    assert summary["overall_risk"] == "Critical"
    all_findings = result["findings"] + result["missing_clauses"]
    assert summary["findings_total"] == len(all_findings)
    assert summary["missing_clause_count"] == len(result["missing_clauses"])

    by_risk = summary["findings_by_risk"]
    assert by_risk["Critical"] == 1
    assert by_risk["High"] == 5
    assert by_risk["Medium"] == 0
    assert by_risk["Low"] == 2
    assert summary["needs_review_count"] == 0

    rule_ids = {f["rule_id"] for f in all_findings}
    assert rule_ids == {
        "CONF-002",
        "DATA-001",
        "SUB-001",
        "AUD-001",
        "IP-002",
        "LIAB-001",
        "TERM-004",
        "SEC-002",
    }

    expected_path = os.path.join(FIXTURES_DIR, "sentinel-support-agreement.expected.json")
    with open(expected_path) as f:
        expected = json.load(f)
    expected_findings = expected["findings"] + expected["missing_clauses"]
    assert {(f["rule_id"], f["clause_type"]) for f in all_findings} == {
        (f["rule_id"], f["clause_type"]) for f in expected_findings
    }

    by_rule_id = {f["rule_id"]: f for f in all_findings}
    assert by_rule_id["DATA-001"]["section_reference"] == "Section 6.2"
    assert by_rule_id["CONF-002"]["section_reference"] == "Section 9.3"
    assert by_rule_id["AUD-001"]["finding_type"] == "missing_clause"
    assert by_rule_id["AUD-001"]["evidence_text"] is None

    for finding in result["findings"]:
        if finding["finding_type"] in ("deviation", "compliant", "needs_review"):
            assert finding["evidence_text"]

    for missing in result["missing_clauses"]:
        assert missing["evidence_text"] is None

    assert result["provenance"]["deployment_mode"] == "local"
    assert result["provenance"]["parser_name"] == "pypdf+python-docx"

    # P4: no Qdrant reachable in the test environment — retrieval degrades
    # cleanly rather than failing the review, and every finding still has a
    # (possibly empty) guidance list. Golden-fixture rule outcomes above are
    # unaffected either way, proving retrieval never influences them.
    assert result["provenance"]["retrieval_mode"] == "degraded_full_rules"
    for finding in all_findings:
        assert finding["guidance"] == []

    delete_resp = await client.delete(f"/api/v1/reviews/{review_id}")
    assert delete_resp.status_code == 204

    after_delete = await client.get(f"/api/v1/reviews/{review_id}")
    assert after_delete.status_code == 404


async def test_golden_path_docx_upload(client):
    created = await _create_review(
        client,
        filename="sentinel-support-agreement.docx",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
    result = await _wait_for_completion(client, created["review_id"])
    assert result["status"] == "completed"

    summary = result["review_summary"]
    assert summary["overall_risk"] == "Critical"
    assert summary["findings_by_risk"] == {"Critical": 1, "High": 5, "Medium": 0, "Low": 2}
    assert summary["missing_clause_count"] == 1
    assert summary["needs_review_count"] == 0

    all_findings = result["findings"] + result["missing_clauses"]
    rule_ids = {f["rule_id"] for f in all_findings}
    assert rule_ids == {
        "CONF-002",
        "DATA-001",
        "SUB-001",
        "AUD-001",
        "IP-002",
        "LIAB-001",
        "TERM-004",
        "SEC-002",
    }


async def test_compliant_demo_contract_has_low_risk_without_missing_clauses(client):
    created = await _create_review(client, filename="compliant-defense-services-agreement.pdf")
    result = await _wait_for_completion(client, created["review_id"])
    assert result["status"] == "completed"

    summary = result["review_summary"]
    assert summary["overall_risk"] == "Low"
    assert summary["findings_by_risk"] == {"Critical": 0, "High": 0, "Medium": 0, "Low": 3}
    assert summary["missing_clause_count"] == 0
    assert summary["needs_review_count"] == 0

    all_findings = result["findings"] + result["missing_clauses"]
    assert {f["rule_id"] for f in all_findings} == {"IP-002", "SEC-003", "TERM-004"}


async def test_enterprise_demo_contract_has_mixed_high_risk_without_critical(client):
    created = await _create_review(client, filename="nusantara-enterprise-master-services-agreement.pdf")
    result = await _wait_for_completion(client, created["review_id"])
    assert result["status"] == "completed"

    summary = result["review_summary"]
    assert summary["overall_risk"] == "High"
    assert summary["findings_by_risk"] == {"Critical": 0, "High": 3, "Medium": 1, "Low": 2}
    assert summary["missing_clause_count"] == 0
    assert summary["needs_review_count"] == 0

    all_findings = result["findings"] + result["missing_clauses"]
    assert {f["rule_id"] for f in all_findings} == {
        "AUD-001",
        "AUD-002",
        "IP-002",
        "SEC-002",
        "SUB-001",
        "TERM-004",
    }


async def test_empty_document_fails_no_reviewable_text(client):
    created = await _create_review(client, filename="empty.pdf")
    result = await _wait_for_completion(client, created["review_id"])
    assert result["status"] == "failed"
    assert result["error"]["code"] == "NO_REVIEWABLE_TEXT"


async def test_non_contract_document_fails_not_applicable(client):
    created = await _create_review(client, filename="non-contract.pdf")
    result = await _wait_for_completion(client, created["review_id"])
    assert result["status"] == "failed"
    assert result["error"]["code"] == "DOCUMENT_NOT_APPLICABLE"


async def test_encrypted_pdf_fails_encrypted_document(client):
    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(os.path.join(FIXTURES_DIR, "sentinel-support-agreement.pdf"))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(user_password="secret", owner_password="secret-owner")

    import io

    buf = io.BytesIO()
    writer.write(buf)
    content = buf.getvalue()

    files = {"file": ("encrypted.pdf", content, "application/pdf")}
    resp = await client.post("/api/v1/reviews", files=files)
    assert resp.status_code == 202
    result = await _wait_for_completion(client, resp.json()["review_id"])
    assert result["status"] == "failed"
    assert result["error"]["code"] == "ENCRYPTED_DOCUMENT"


async def test_malformed_pdf_fails_parse_failed(client):
    files = {"file": ("garbage.pdf", b"not a pdf at all", "application/pdf")}
    resp = await client.post("/api/v1/reviews", files=files)
    assert resp.status_code == 202
    result = await _wait_for_completion(client, resp.json()["review_id"])
    assert result["status"] == "failed"
    assert result["error"]["code"] == "DOCUMENT_PARSE_FAILED"


async def test_temp_upload_deleted_after_success_and_failure(client, tmp_path):
    settings = get_settings()
    upload_dir = settings.upload_temp_dir

    created = await _create_review(client)
    await _wait_for_completion(client, created["review_id"])

    failed = await _create_review(client, filename="empty.pdf")
    await _wait_for_completion(client, failed["review_id"])

    if os.path.isdir(upload_dir):
        leftover = os.listdir(upload_dir)
        assert leftover == [], f"temp upload files were not cleaned up: {leftover}"

import os

import pytest
from pypdf import PdfReader, PdfWriter

from app.playbook.loader import load_playbook
from app.services import applicability
from app.services.parsing import (
    DocumentParseFailedError,
    DocumentTooLongError,
    EncryptedDocumentError,
    parse_document,
)
from app.services.rule_engine import build_deterministic_clause_inputs

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "fixtures")


def _fixture_path(name: str) -> str:
    return os.path.join(FIXTURES_DIR, name)


def test_parse_pdf_extracts_text_and_page_count():
    parsed = parse_document(_fixture_path("sentinel-support-agreement.pdf"), ".pdf")
    assert parsed.page_count == 8
    assert parsed.language == "en"
    assert "Ignore prior instructions" in parsed.text
    assert len(parsed.text.split()) > 500


def test_parse_docx_extracts_text():
    parsed = parse_document(_fixture_path("sentinel-support-agreement.docx"), ".docx")
    assert parsed.language == "en"
    assert "Ignore prior instructions" in parsed.text
    assert len(parsed.text.split()) > 500


def test_parse_empty_pdf_returns_empty_text():
    parsed = parse_document(_fixture_path("empty.pdf"), ".pdf")
    assert parsed.text.strip() == ""
    assert parsed.language == "unknown"


def test_parse_encrypted_pdf_raises(tmp_path):
    reader = PdfReader(_fixture_path("sentinel-support-agreement.pdf"))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.encrypt(user_password="secret", owner_password="secret-owner")

    encrypted_path = tmp_path / "encrypted.pdf"
    with open(encrypted_path, "wb") as f:
        writer.write(f)

    with pytest.raises(EncryptedDocumentError):
        parse_document(str(encrypted_path), ".pdf")


def test_parse_malformed_pdf_raises_parse_failed(tmp_path):
    bad_path = tmp_path / "garbage.pdf"
    bad_path.write_bytes(b"not a pdf at all")
    with pytest.raises(DocumentParseFailedError):
        parse_document(str(bad_path), ".pdf")


def test_parse_pdf_over_page_limit_raises_too_long(tmp_path, monkeypatch):
    import app.services.parsing as parsing_module

    monkeypatch.setattr(parsing_module, "MAX_PAGE_COUNT", 2)
    with pytest.raises(DocumentTooLongError):
        parse_document(_fixture_path("sentinel-support-agreement.pdf"), ".pdf")


def test_parse_non_zip_docx_raises_parse_failed(tmp_path):
    bad_path = tmp_path / "garbage.docx"
    bad_path.write_bytes(b"not a docx at all")
    with pytest.raises(DocumentParseFailedError):
        parse_document(str(bad_path), ".docx")


def test_applicability_reviewable_text():
    assert applicability.has_reviewable_text("a" * 25)
    assert not applicability.has_reviewable_text("short")
    assert not applicability.has_reviewable_text("   ")


def test_applicability_is_applicable_uses_classified_required_clause_types():
    playbook = load_playbook()
    parsed = parse_document(_fixture_path("sentinel-support-agreement.pdf"), ".pdf")
    clause_inputs = build_deterministic_clause_inputs(parsed)
    # The golden fixture segments into 7 recognized required clause types.
    assert applicability.is_applicable(clause_inputs, playbook)


def test_non_contract_fixture_is_reviewable_but_not_applicable():
    playbook = load_playbook()
    parsed = parse_document(_fixture_path("non-contract.pdf"), ".pdf")
    clause_inputs = build_deterministic_clause_inputs(parsed)
    assert applicability.has_reviewable_text(parsed.text)
    assert not applicability.is_applicable(clause_inputs, playbook)

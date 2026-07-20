from app.services.attribute_extraction import extract_attributes
from app.services.segmentation import segment_document

FIXTURE_LIKE_TEXT = (
    "Section 6. Data Handling\n"
    "6.1 Supplier shall process Customer Data only as necessary.\n"
    "6.2 The Supplier may process Customer Data using regional public cloud services and "
    "shall not transfer Customer Data outside the region without prior written consent.\n"
    "6.3 Supplier shall maintain a current record of processing activities.\n"
    "Section 9. Confidentiality\n"
    "9.3 The Supplier may disclose Confidential Information to its Affiliates for purposes "
    "related to this Agreement.\n"
    "Section 20. Unmatched Wording\n"
)


def _segment_for(clause_type: str):
    segments = segment_document(FIXTURE_LIKE_TEXT, [0])
    return next(s for s in segments if s.clause_type == clause_type)


def test_data_handling_extraction_matches_fixture_wording():
    result = extract_attributes(_segment_for("data_handling"))
    assert result.attributes["external_cloud_allowed"] is True
    assert result.attributes["cross_border_allowed"] is False
    assert result.attributes["prior_approval_required"] is True
    assert result.confidence >= 0.80
    assert result.section_reference == "Section 6.2"


def test_confidentiality_extraction_matches_fixture_wording():
    result = extract_attributes(_segment_for("confidentiality"))
    assert result.attributes["disclosure_scope"] == "affiliates"
    assert result.attributes["need_to_know_required"] is False
    assert result.attributes["equivalent_obligations_required"] is False
    assert result.confidence >= 0.80


def test_unmatched_wording_yields_low_confidence():
    """A recognized clause_type heading whose body doesn't contain any known
    trigger phrase should extract with low confidence, not a false positive
    high-confidence match. This exercises the REV-001 confidence boundary."""
    text = "Section 9. Confidentiality\nThis clause discusses matters unrelated to any known trigger phrase.\n"
    segments = segment_document(text, [0])
    result = extract_attributes(segments[0])
    assert result.confidence < 0.60
    assert result.attributes["disclosure_scope"] == "unknown"


def test_intellectual_property_evidence_spans_full_multi_sentence_subclause():
    text = (
        "Section 13. Intellectual Property\n"
        "13.1 The Buyer owns all bespoke Deliverables created under this Agreement. The "
        "Supplier retains ownership of pre-existing Background IP and grants the Buyer a "
        "perpetual, irrevocable license to use Background IP embedded in the Deliverables.\n"
    )
    segments = segment_document(text, [0])
    result = extract_attributes(segments[0])
    assert result.attributes["bespoke_owner"] == "customer"
    assert result.attributes["background_ip_retained_by_vendor"] is True
    assert result.attributes["customer_license_sufficient"] is True
    assert "perpetual, irrevocable license" in result.evidence_text
    assert result.section_reference == "Section 13.1"


def test_audit_present_but_insufficient():
    text = (
        "Section 10. Audit\n"
        "10.1 The Supplier shall provide vendor-selected summary reports upon request. "
        "Independent evidence is not permitted.\n"
    )
    segments = segment_document(text, [0])
    result = extract_attributes(segments[0])
    assert result.attributes["customer_audit_right"] is False
    assert result.attributes["vendor_summary_only"] is True

from app.services.segmentation import find_subclause_reference, segment_document, subclause_evidence

SAMPLE_TEXT = (
    "Cover Page\n"
    "Section 1. Definitions\n"
    "Some definitions here.\n"
    "Section 6. Data Handling\n"
    "6.1 Supplier shall process data per instructions.\n"
    "6.2 The Supplier may process Customer Data using regional public cloud services.\n"
    "Section 7. Reserved\n"
    "Nothing to see here.\n"
    "Section 9. Confidentiality\n"
    "9.1 General confidentiality duty.\n"
    "9.3 The Supplier may disclose Confidential Information to its Affiliates.\n"
)
PAGE_BOUNDARIES = [0]  # single page for this synthetic test


def test_segments_recognized_headings_only():
    segments = segment_document(SAMPLE_TEXT, PAGE_BOUNDARIES)
    clause_types = [s.clause_type for s in segments]
    assert clause_types == ["data_handling", "confidentiality"]


def test_unrecognized_headings_are_skipped():
    segments = segment_document(SAMPLE_TEXT, PAGE_BOUNDARIES)
    headings = [s.heading for s in segments]
    assert "Reserved" not in headings
    assert "Definitions" not in headings


def test_section_reference_and_page():
    segments = segment_document(SAMPLE_TEXT, PAGE_BOUNDARIES)
    data_seg = segments[0]
    assert data_seg.section_reference == "Section 6"
    assert data_seg.page_start == 1
    assert data_seg.page_end == 1


def test_subclause_reference_resolves_nearest_marker():
    segments = segment_document(SAMPLE_TEXT, PAGE_BOUNDARIES)
    data_seg = segments[0]
    offset = data_seg.text.find("regional public cloud")
    assert find_subclause_reference(data_seg, offset) == "Section 6.2"


def test_subclause_reference_falls_back_to_section_when_before_any_marker():
    text = "Section 6. Data Handling\nSome preamble text before any numbered sub-clause.\n6.1 Supplier shall process data.\n"
    segments = segment_document(text, [0])
    data_seg = segments[0]
    preamble_offset = data_seg.text.find("preamble")
    assert find_subclause_reference(data_seg, preamble_offset) == "Section 6"


def test_subclause_evidence_spans_full_subclause_not_one_sentence():
    text = "Section 13. Intellectual Property\n13.1 First sentence here. Second sentence continues the same item.\n"
    segments = segment_document(text, [0])
    seg = segments[0]
    offset = seg.text.find("First sentence")
    evidence, reference = subclause_evidence(seg, offset)
    assert evidence == "First sentence here. Second sentence continues the same item."
    assert reference == "Section 13.1"


def test_whitespace_is_normalized_across_line_wraps():
    text = "Section 8. Security\n8.1 The Supplier shall maintain safeguards consistent with industry\nstandards.\n"
    segments = segment_document(text, [0])
    seg = segments[0]
    assert "industry standards" in seg.text
    assert "industry\nstandards" not in seg.text

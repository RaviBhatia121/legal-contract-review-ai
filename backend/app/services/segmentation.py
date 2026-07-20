"""Deterministic, fixture-oriented clause segmentation (P2).

This segmenter recognizes the heading convention used by the generated
`sentinel-support-agreement` fixture (`scripts/generate_fixtures.py`):
top-level headings of the form "Section N. <Title>" or "Appendix X. <Title>"
at the start of a line, with numbered sub-clauses like "6.2 <text>" inside
the section body.

**This is not a general contract parser.** It recognizes this fixture's
heading/numbering convention only. A real contract with different structure
(no numbered sections, different heading style, embedded tables, etc.) will
not segment correctly here. Real, general clause segmentation is P3 scope
(model-assisted, see MODEL_AND_PIPELINE_CONTRACT.md); this module exists so
P2 can demonstrate the deterministic rule engine end to end against the
committed synthetic fixture, per IMPLEMENTATION_PHASE_PLAN.md's P2 boundary.
"""

import re
from dataclasses import dataclass

from app.services.parsing import page_for_offset

_HEADING_RE = re.compile(r"^(?:Section \d+\.|Appendix [A-Z]\.)\s+(.+)$", re.MULTILINE)
_SUBCLAUSE_RE = re.compile(r"(?<![\d.])(\d{1,2}\.\d{1,2})\s")

# First matching keyword (case-insensitive substring of the heading title)
# wins. Order matters only where a title could match more than one keyword.
_HEADING_KEYWORDS: tuple[tuple[str, str], ...] = (
    ("confidentiality", "confidentiality"),
    ("data handling", "data_handling"),
    ("subcontract", "subcontracting"),
    ("audit", "audit_inspection"),
    ("inspection", "audit_inspection"),
    ("intellectual property", "intellectual_property"),
    ("liability", "liability_indemnity"),
    ("termination", "termination_exit"),
    ("security", "security_incident"),
)


@dataclass(frozen=True)
class ClauseSegment:
    clause_type: str
    heading: str
    section_reference: str
    page_start: int
    page_end: int
    text: str
    start_offset: int


def _clause_type_for_heading(title: str) -> str | None:
    lowered = title.lower()
    for keyword, clause_type in _HEADING_KEYWORDS:
        if keyword in lowered:
            return clause_type
    return None


def segment_document(text: str, page_boundaries: list[int]) -> list[ClauseSegment]:
    """Split parsed document text into recognized clause segments.

    Headings that don't map to a known clause type (e.g. "Parties and
    Recitals", "Section 7. Reserved") are skipped — they contribute no
    segment and therefore no clause, which is correct: only recognized
    clause-type sections should be treated as evidence.
    """
    matches = list(_HEADING_RE.finditer(text))
    segments: list[ClauseSegment] = []

    for i, match in enumerate(matches):
        title = match.group(1).strip()
        clause_type = _clause_type_for_heading(title)
        if clause_type is None:
            continue

        body_start = match.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        # Whitespace-normalized so phrase matching in attribute_extraction
        # isn't broken by mid-sentence PDF line wraps (extracted text
        # preserves the PDF's rendered line breaks, which can fall inside a
        # sentence). Page attribution already uses absolute offsets in the
        # original document text computed above, so this is safe.
        body_text = re.sub(r"\s+", " ", text[body_start:body_end]).strip()

        section_number_match = re.match(r"Section (\d+)\.", text[match.start() : match.end()])
        section_reference = f"Section {section_number_match.group(1)}" if section_number_match else title

        page_start = page_for_offset(match.start(), page_boundaries)
        page_end = page_for_offset(body_end - 1 if body_end > body_start else body_start, page_boundaries)

        segments.append(
            ClauseSegment(
                clause_type=clause_type,
                heading=title,
                section_reference=section_reference,
                page_start=page_start,
                page_end=page_end,
                text=body_text,
                start_offset=body_start,
            )
        )

    return segments


def find_subclause_reference(segment: ClauseSegment, local_offset: int) -> str:
    """Return the nearest preceding numbered sub-clause reference (e.g. "Section 6.2"),
    falling back to the segment's top-level section_reference if none precedes the offset.
    """
    _, _, number = _subclause_bounds(segment, local_offset)
    return f"Section {number}" if number else segment.section_reference


def _subclause_bounds(segment: ClauseSegment, local_offset: int) -> tuple[int, int, str | None]:
    """Return (body_start, body_end, subclause_number) for the numbered
    sub-clause containing local_offset within segment.text (already
    whitespace-normalized). subclause_number is None if local_offset
    precedes any recognized sub-clause marker.
    """
    marks = list(_SUBCLAUSE_RE.finditer(segment.text))
    body_start = 0
    number: str | None = None
    for m in marks:
        if m.start() > local_offset:
            break
        body_start = m.end()
        number = m.group(1)

    body_end = len(segment.text)
    for m in marks:
        if m.start() >= body_start:
            body_end = m.start()
            break

    return body_start, body_end, number


def subclause_evidence(segment: ClauseSegment, local_offset: int) -> tuple[str, str]:
    """Return (evidence_text, section_reference) for the full numbered
    sub-clause containing local_offset — used as Finding.evidence_text so a
    multi-sentence sub-clause (e.g. IP ownership + license in one numbered
    item) is reported whole rather than truncated to one sentence.
    """
    body_start, body_end, number = _subclause_bounds(segment, local_offset)
    evidence_text = segment.text[body_start:body_end].strip()
    section_reference = f"Section {number}" if number else segment.section_reference
    return evidence_text, section_reference

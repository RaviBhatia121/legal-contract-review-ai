"""General (non-fixture-tuned) text-block splitter (P3).

Unlike P2's `segmentation.py` (which recognizes one fixture's specific
heading convention), this splitter makes no assumption about document
structure — it works on any PDF/DOCX text. It only chunks text into
page-attributed blocks small enough for reliable model attention; the model
itself does the semantic work of grouping blocks into clauses (P-01 in
PROMPT_SPEC.md), not this splitter.

Strategy: prefer blank-line paragraph boundaries (present in DOCX
extraction); when text has no blank-line structure at all (common for PDF
extraction, which joins wrapped lines with single newlines), fall back to
accumulating lines up to a soft length cap. Either way, long blocks are
further split at sentence boundaries so no block exceeds the cap.
"""

import re
from dataclasses import dataclass

from app.services.parsing import page_for_offset

_DEFAULT_MAX_BLOCK_CHARS = 800
_BLANK_LINE_RE = re.compile(r"\n\s*\n")
_SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?])\s+")


@dataclass(frozen=True)
class TextBlockSpan:
    text: str
    start_offset: int
    end_offset: int


def split_into_blocks(text: str, max_block_chars: int = _DEFAULT_MAX_BLOCK_CHARS) -> list[TextBlockSpan]:
    paragraphs = _split_paragraphs(text)
    blocks: list[TextBlockSpan] = []
    for para_text, para_start in paragraphs:
        if not para_text.strip():
            continue
        blocks.extend(_split_long(para_text, para_start, max_block_chars))
    return blocks


def _split_paragraphs(text: str) -> list[tuple[str, int]]:
    if _BLANK_LINE_RE.search(text):
        return _split_on_pattern(text, _BLANK_LINE_RE)
    return _chunk_lines(text)


def _split_on_pattern(text: str, pattern: re.Pattern) -> list[tuple[str, int]]:
    results: list[tuple[str, int]] = []
    offset = 0
    for part in pattern.split(text):
        idx = text.find(part, offset)
        if idx == -1:
            idx = offset
        results.append((part, idx))
        offset = idx + len(part)
    return results


def _chunk_lines(text: str, max_chars: int = _DEFAULT_MAX_BLOCK_CHARS) -> list[tuple[str, int]]:
    lines = text.split("\n")
    results: list[tuple[str, int]] = []
    offset = 0
    current_lines: list[str] = []
    current_start = 0
    current_len = 0

    for line in lines:
        line_start = offset
        offset += len(line) + 1  # +1 for the newline consumed by split
        if not current_lines:
            current_start = line_start
        if current_len + len(line) > max_chars and current_lines:
            results.append(("\n".join(current_lines), current_start))
            current_lines = []
            current_len = 0
            current_start = line_start
        current_lines.append(line)
        current_len += len(line) + 1

    if current_lines:
        results.append(("\n".join(current_lines), current_start))
    return results


def _split_long(text: str, start_offset: int, max_chars: int) -> list[TextBlockSpan]:
    if len(text) <= max_chars:
        return [TextBlockSpan(text=text.strip(), start_offset=start_offset, end_offset=start_offset + len(text))]

    spans: list[TextBlockSpan] = []
    sentences = _SENTENCE_BOUNDARY_RE.split(text)
    offset = start_offset
    current = ""
    current_start = offset
    for sentence in sentences:
        idx = text.find(sentence, offset - start_offset) + start_offset
        if len(current) + len(sentence) > max_chars and current:
            spans.append(TextBlockSpan(text=current.strip(), start_offset=current_start, end_offset=idx))
            current = ""
            current_start = idx
        current = f"{current} {sentence}".strip()
        offset = idx + len(sentence)
    if current.strip():
        spans.append(TextBlockSpan(text=current.strip(), start_offset=current_start, end_offset=start_offset + len(text)))
    return spans


def blocks_with_pages(text: str, page_boundaries: list[int], max_block_chars: int = _DEFAULT_MAX_BLOCK_CHARS):
    """Yield (block_id, text, page_start, page_end) tuples ready for TextBlock construction."""
    for i, span in enumerate(split_into_blocks(text, max_block_chars)):
        page_start = page_for_offset(span.start_offset, page_boundaries)
        page_end = page_for_offset(max(span.end_offset - 1, span.start_offset), page_boundaries)
        yield f"b{i}", span.text, page_start, page_end

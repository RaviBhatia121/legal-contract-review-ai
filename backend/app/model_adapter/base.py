"""Provider-neutral model adapter interface (P3).

Only `OllamaAdapter` (ollama_adapter.py) is implemented. Cloud providers
(Anthropic/OpenAI/Gemini) are deliberately NOT implemented here — see
`DATA_MODEL.md`'s provider_type enum and `UI_SPEC.md`'s "Not enabled"
convention. Adding a cloud adapter is P5 scope (D-05), not silently
introduced by this interface existing.
"""

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class TextBlock:
    block_id: str
    text: str
    page_start: int
    page_end: int


@dataclass(frozen=True)
class ClassifiedClause:
    clause_id: str
    clause_type: str
    title: str
    section_reference: str | None
    page_start: int | None
    page_end: int | None
    extracted_text: str
    classification_confidence: float


@dataclass(frozen=True)
class AttributeResult:
    raw_attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PingResult:
    ok: bool
    latency_ms: int
    model_name: str


class ModelAdapter(Protocol):
    provider_type: str
    model_name: str

    async def classify_blocks(self, blocks: list[TextBlock], clause_types: list[str]) -> list[ClassifiedClause]: ...

    async def extract_attributes(self, clause: ClassifiedClause, attribute_names: list[str]) -> AttributeResult: ...

    async def ping(self) -> PingResult: ...

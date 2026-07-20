"""Haystack pipeline components (P3).

Two thin async components wrapping `ModelAdapter` calls — they hold no
extraction logic themselves, only routing and validation, per
TECH_STACK_AND_LICENSES.md's "explicit pipeline components and routing."

The pipeline is assembled in Python code only, inside
`ClauseIntelligenceService`, and only ever built lazily on first use — never
at module import time, so app startup does not depend on Ollama being
reachable, and never deserialized from configuration or user input, per
SECURITY_AND_DATA.md's rule against loading pipeline definitions from
untrusted input.

Haystack 2.x components require both a synchronous `run` (used for output
type introspection) and a separate `run_async` coroutine with the same
signature; `AsyncPipeline` auto-detects and calls `run_async` when present.
The sync `run` here is an intentional stub — this pipeline is async-only.
"""

from haystack import component

from app.model_adapter.base import AttributeResult, ClassifiedClause, ModelAdapter, TextBlock


@component
class ClauseClassifierComponent:
    def __init__(self, adapter: ModelAdapter, clause_types: list[str]):
        self._adapter = adapter
        self._clause_types = clause_types

    @component.output_types(clauses=list[ClassifiedClause])
    def run(self, blocks: list[TextBlock]):
        raise NotImplementedError("ClauseClassifierComponent is async-only; use run_async via AsyncPipeline.")

    @component.output_types(clauses=list[ClassifiedClause])
    async def run_async(self, blocks: list[TextBlock]):
        clauses = await self._adapter.classify_blocks(blocks, self._clause_types)
        return {"clauses": clauses}


@component
class AttributeExtractorComponent:
    def __init__(self, adapter: ModelAdapter, attribute_names_by_type: dict[str, list[str]]):
        self._adapter = adapter
        self._attribute_names_by_type = attribute_names_by_type

    @component.output_types(extractions=list)
    def run(self, clauses: list[ClassifiedClause]):
        raise NotImplementedError("AttributeExtractorComponent is async-only; use run_async via AsyncPipeline.")

    @component.output_types(extractions=list)
    async def run_async(self, clauses: list[ClassifiedClause]):
        extractions: list[tuple[ClassifiedClause, AttributeResult]] = []
        for clause in clauses:
            names = self._attribute_names_by_type.get(clause.clause_type)
            if not names:
                continue  # unmapped/unknown clause_type: nothing to extract
            result = await self._adapter.extract_attributes(clause, names)
            extractions.append((clause, result))
        return {"extractions": extractions}

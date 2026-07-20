"""Extraction-path selector (P3).

Produces `ClauseInput`s (see `rule_engine.py`) from either:
- the P2 deterministic, fixture-oriented path (`rule_engine.build_deterministic_clause_inputs`), or
- the P3 model-assisted path (Haystack pipeline over `OllamaAdapter`),

selected by `Settings.clause_intelligence_mode` ("deterministic" | "model"),
which defaults to "deterministic" everywhere. Deterministic is the only mode
that runs without a reachable model — this service builds nothing until
`get_clause_inputs` is actually called in "model" mode, so app startup never
depends on Ollama being reachable (the Haystack pipeline is constructed
lazily on first use, not at import time).

Rule evaluation itself is not this service's job — callers pass the returned
`ClauseInput`s to `rule_engine.evaluate_clauses`.
"""

from haystack import AsyncPipeline

from app.core.config import Settings
from app.model_adapter.base import TextBlock
from app.model_adapter.ollama_adapter import OllamaAdapter
from app.playbook.loader import Playbook
from app.schemas.clause_attributes import attribute_names_for, normalize_attributes
from app.services.block_splitter import blocks_with_pages
from app.services.haystack_pipeline import AttributeExtractorComponent, ClauseClassifierComponent
from app.services.parsing import ParsedDocument
from app.services.rule_engine import ClauseInput, build_deterministic_clause_inputs

DETERMINISTIC_MODE = "deterministic"
MODEL_MODE = "model"

# Source label written onto evidence-based findings when extraction came from
# the model path; missing-clause findings always stay "rule" regardless (see
# rule_engine._make_finding).
MODEL_ASSISTED_SOURCE = "model_assisted_rule"
DETERMINISTIC_SOURCE = "rule"


class ClauseIntelligenceService:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._adapter: OllamaAdapter | None = None

    def _get_adapter(self) -> OllamaAdapter:
        if self._adapter is None:
            self._adapter = OllamaAdapter(
                base_url=self._settings.ollama_base_url,
                model_name=self._settings.model_name,
                timeout_s=self._settings.ollama_timeout_s,
            )
        return self._adapter

    def _build_pipeline(self, playbook: Playbook):
        # Built fresh per call, not cached at instance/import scope: cheap
        # (no network I/O happens until run_async), and avoids holding a
        # pipeline bound to a stale playbook/adapter across requests. Still
        # satisfies "no construction at module import time" — this method
        # only runs when a review actually reaches the model path.
        adapter = self._get_adapter()
        clause_types = [ct for ct in playbook.clause_types if ct != "unknown"]
        attribute_names_by_type = {ct: attribute_names_for(ct) for ct in clause_types}

        pipeline = AsyncPipeline()
        pipeline.add_component("classify", ClauseClassifierComponent(adapter, clause_types))
        pipeline.add_component("extract", AttributeExtractorComponent(adapter, attribute_names_by_type))
        pipeline.connect("classify.clauses", "extract.clauses")
        return pipeline

    async def get_clause_inputs(self, parsed: ParsedDocument, playbook: Playbook) -> tuple[list[ClauseInput], str]:
        """Returns (clause_inputs, mode_used). mode_used drives Finding.source
        in the caller (job_runner.py)."""
        if self._settings.clause_intelligence_mode == MODEL_MODE:
            return await self._model_clause_inputs(parsed, playbook), MODEL_MODE
        return build_deterministic_clause_inputs(parsed), DETERMINISTIC_MODE

    async def _model_clause_inputs(self, parsed: ParsedDocument, playbook: Playbook) -> list[ClauseInput]:
        pipeline = self._build_pipeline(playbook)
        blocks = [
            TextBlock(block_id=bid, text=text, page_start=ps, page_end=pe)
            for bid, text, ps, pe in blocks_with_pages(parsed.text, parsed.page_boundaries)
        ]
        result = await pipeline.run_async({"classify": {"blocks": blocks}})
        extractions = result["extract"]["extractions"]

        clause_inputs: list[ClauseInput] = []
        for clause, attr_result in extractions:
            normalized = normalize_attributes(clause.clause_type, attr_result.raw_attributes)
            clause_inputs.append(
                ClauseInput(
                    clause_type=clause.clause_type,
                    title=clause.title,
                    section_reference=clause.section_reference or f"page {clause.page_start}",
                    page_start=clause.page_start or 1,
                    page_end=clause.page_end or clause.page_start or 1,
                    evidence_text=clause.extracted_text,
                    confidence=clause.classification_confidence,
                    attributes=normalized,
                )
            )
        return clause_inputs

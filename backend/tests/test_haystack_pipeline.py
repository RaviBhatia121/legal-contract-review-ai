"""Haystack pipeline component tests with a fake ModelAdapter (no HTTP, no
Ollama) — proves the components wire together correctly via AsyncPipeline."""

import pytest
from haystack import AsyncPipeline

from app.model_adapter.base import AttributeResult, ClassifiedClause, TextBlock
from app.services.haystack_pipeline import AttributeExtractorComponent, ClauseClassifierComponent

pytestmark = pytest.mark.asyncio


class _FakeAdapter:
    provider_type = "fake"
    model_name = "fake-model"

    async def classify_blocks(self, blocks, clause_types):
        return [
            ClassifiedClause(
                clause_id="c1",
                clause_type="data_handling",
                title="Data Handling",
                section_reference="Section 6",
                page_start=blocks[0].page_start,
                page_end=blocks[0].page_end,
                extracted_text=blocks[0].text,
                classification_confidence=0.9,
            )
        ]

    async def extract_attributes(self, clause, names):
        return AttributeResult(raw_attributes={name: "unknown" for name in names})


async def test_pipeline_wires_classify_to_extract():
    adapter = _FakeAdapter()
    pipe = AsyncPipeline()
    pipe.add_component("classify", ClauseClassifierComponent(adapter, ["data_handling"]))
    pipe.add_component(
        "extract", AttributeExtractorComponent(adapter, {"data_handling": ["present", "external_cloud_allowed"]})
    )
    pipe.connect("classify.clauses", "extract.clauses")

    result = await pipe.run_async({"classify": {"blocks": [TextBlock("b0", "some clause text", 1, 1)]}})
    extractions = result["extract"]["extractions"]
    assert len(extractions) == 1
    clause, attr_result = extractions[0]
    assert clause.clause_type == "data_handling"
    assert attr_result.raw_attributes == {"present": "unknown", "external_cloud_allowed": "unknown"}


async def test_attribute_extractor_skips_unmapped_clause_type():
    adapter = _FakeAdapter()
    component = AttributeExtractorComponent(adapter, {})  # no attribute names configured for any type
    result = await component.run_async(
        clauses=[
            ClassifiedClause("c1", "data_handling", "Data", "Section 6", 1, 1, "text", 0.9),
        ]
    )
    assert result["extractions"] == []


async def test_sync_run_is_not_implemented_by_design():
    adapter = _FakeAdapter()
    component = ClauseClassifierComponent(adapter, ["data_handling"])
    with pytest.raises(NotImplementedError):
        component.run(blocks=[])

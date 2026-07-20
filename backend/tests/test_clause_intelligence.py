import pytest

from app.core.config import Settings
from app.model_adapter.base import AttributeResult, ClassifiedClause
from app.playbook.loader import load_playbook
from app.services.clause_intelligence import DETERMINISTIC_MODE, MODEL_MODE, ClauseIntelligenceService
from app.services.parsing import ParsedDocument
from app.services.rule_engine import build_deterministic_clause_inputs

pytestmark = pytest.mark.asyncio


class _FakeAdapter:
    provider_type = "ollama"
    model_name = "fake-model"

    async def classify_blocks(self, blocks, clause_types):
        return [
            ClassifiedClause("c1", "data_handling", "Data", "Section 6", 1, 1, "external cloud allowed", 0.91),
        ]

    async def extract_attributes(self, clause, names):
        return AttributeResult(raw_attributes={"present": True, "external_cloud_allowed": True})


async def test_deterministic_mode_matches_build_deterministic_clause_inputs():
    settings = Settings(clause_intelligence_mode=DETERMINISTIC_MODE)
    service = ClauseIntelligenceService(settings)
    playbook = load_playbook()
    parsed = ParsedDocument(
        text="Section 6. Data Handling\n6.2 The Supplier may process Customer Data using regional public cloud.\n",
        page_count=1,
        language="en",
        page_boundaries=[0],
    )
    clause_inputs, mode_used = await service.get_clause_inputs(parsed, playbook)
    assert mode_used == DETERMINISTIC_MODE
    expected = build_deterministic_clause_inputs(parsed)
    assert [ci.clause_type for ci in clause_inputs] == [ci.clause_type for ci in expected]


async def test_model_mode_uses_adapter_and_normalizes_attributes():
    settings = Settings(clause_intelligence_mode=MODEL_MODE)
    service = ClauseIntelligenceService(settings)
    service._adapter = _FakeAdapter()  # inject fake, skip real HTTP entirely
    playbook = load_playbook()
    parsed = ParsedDocument(text="Some contract text about data handling.\n", page_count=1, language="en", page_boundaries=[0])

    clause_inputs, mode_used = await service.get_clause_inputs(parsed, playbook)
    assert mode_used == MODEL_MODE
    assert len(clause_inputs) == 1
    ci = clause_inputs[0]
    assert ci.clause_type == "data_handling"
    assert ci.confidence == 0.91
    # normalize_attributes fills in every spec'd attribute, defaulting missing ones to "unknown"
    assert ci.attributes["present"] is True
    assert ci.attributes["external_cloud_allowed"] is True
    assert ci.attributes["cross_border_allowed"] == "unknown"

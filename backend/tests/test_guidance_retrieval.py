"""GuidanceService tests against fake Qdrant/embedder objects — no real
Qdrant or Ollama instance, same no-new-test-dependency pattern as
test_ollama_adapter.py's stdlib mock HTTP server."""

import pytest

from app.core.config import get_settings
from app.playbook.loader import load_playbook
from app.services.embedding_client import EmbeddingUnavailableError
from app.services.guidance_retrieval import DEGRADED_MODE, QDRANT_MODE, GuidanceService, check_qdrant_reachable

pytestmark = pytest.mark.asyncio


class _FakePoint:
    def __init__(self, payload: dict, score: float | None = None):
        self.payload = payload
        self.score = score


class _FakeQueryResult:
    def __init__(self, points: list[_FakePoint]):
        self.points = points


class _FakeQdrantClient:
    def __init__(self, points_by_rule: dict[str, list[_FakePoint]]):
        self._points_by_rule = points_by_rule

    async def get_collections(self):
        return None

    async def query_points(self, collection_name, query, query_filter, limit, with_payload):
        rule_id = query_filter.must[0].match.value
        return _FakeQueryResult(self._points_by_rule.get(rule_id, [])[:limit])

    async def scroll(self, collection_name, scroll_filter, limit, with_payload):
        rule_id = scroll_filter.must[0].match.value
        return self._points_by_rule.get(rule_id, [])[:limit], None


class _UnreachableQdrantClient:
    async def get_collections(self):
        raise ConnectionError("qdrant unreachable")


class _FakeEmbedder:
    async def embed(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]


class _FailingEmbedder:
    async def embed(self, text: str) -> list[float]:
        raise EmbeddingUnavailableError("embedding model unreachable")


def _guidance_point(guidance_id="G-1", score=None) -> _FakePoint:
    return _FakePoint(
        {"id": guidance_id, "text": "sample guidance text", "category": "negotiation_tip", "source_note": "note"},
        score=score,
    )


async def test_retrieve_for_rules_returns_qdrant_mode_with_results():
    playbook = load_playbook()
    rule = playbook.rule_by_id("DATA-001")

    service = GuidanceService(get_settings())
    service._client = _FakeQdrantClient({"DATA-001": [_guidance_point(score=0.8)]})
    service._embedder = _FakeEmbedder()

    result, mode = await service.retrieve_for_rules([rule])

    assert mode == QDRANT_MODE
    assert len(result["DATA-001"]) == 1
    assert result["DATA-001"][0].id == "G-1"
    assert result["DATA-001"][0].score == 0.8


async def test_retrieve_for_rules_falls_back_to_scroll_when_embedding_unavailable():
    playbook = load_playbook()
    rule = playbook.rule_by_id("DATA-001")

    service = GuidanceService(get_settings())
    service._client = _FakeQdrantClient({"DATA-001": [_guidance_point()]})
    service._embedder = _FailingEmbedder()

    result, mode = await service.retrieve_for_rules([rule])

    # Embedding failed but Qdrant answered the reachability probe: still a
    # real Qdrant query (unranked scroll), not a degraded/empty result.
    assert mode == QDRANT_MODE
    assert len(result["DATA-001"]) == 1
    assert result["DATA-001"][0].score is None


async def test_retrieve_for_rules_degrades_when_qdrant_unreachable():
    playbook = load_playbook()
    rule = playbook.rule_by_id("DATA-001")

    service = GuidanceService(get_settings())
    service._client = _UnreachableQdrantClient()

    result, mode = await service.retrieve_for_rules([rule])

    assert result == {}
    assert mode == DEGRADED_MODE


async def test_retrieve_for_rules_empty_input_returns_degraded():
    service = GuidanceService(get_settings())
    result, mode = await service.retrieve_for_rules([])
    assert result == {}
    assert mode == DEGRADED_MODE


async def test_retrieve_for_rules_deduplicates_repeated_rule_ids():
    """Two findings triggered by the same rule_id should query Qdrant once
    per unique rule, not once per finding."""
    playbook = load_playbook()
    rule = playbook.rule_by_id("DATA-001")

    call_count = {"n": 0}

    class _CountingClient(_FakeQdrantClient):
        async def query_points(self, *args, **kwargs):
            call_count["n"] += 1
            return await super().query_points(*args, **kwargs)

    service = GuidanceService(get_settings())
    service._client = _CountingClient({"DATA-001": [_guidance_point()]})
    service._embedder = _FakeEmbedder()

    result, mode = await service.retrieve_for_rules([rule, rule, rule])

    assert mode == QDRANT_MODE
    assert call_count["n"] == 1
    assert len(result) == 1


async def test_check_qdrant_reachable_returns_false_when_unreachable():
    """Real function, real (absent) Qdrant hostname — this is exactly the
    default docker-compose profile's state, and /health/ready must not hang
    or raise when checking it."""
    result = await check_qdrant_reachable(get_settings(), timeout_s=0.5)
    assert result is False


async def test_check_qdrant_reachable_returns_true_when_reachable(monkeypatch):
    class _FakeReachableClient:
        def __init__(self, *args, **kwargs):
            pass

        async def get_collections(self):
            return None

        async def close(self):
            pass

    import app.services.guidance_retrieval as guidance_retrieval_module

    monkeypatch.setattr(guidance_retrieval_module, "AsyncQdrantClient", _FakeReachableClient)

    result = await check_qdrant_reachable(get_settings())
    assert result is True

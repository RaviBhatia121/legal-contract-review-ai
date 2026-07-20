"""Qdrant API-key wiring tests (P6/R-06).

Live-verified separately (see docs/SECURITY_EVIDENCE.md) that Qdrant treats
an *empty-string* API key as "configured" and starts rejecting
unauthenticated requests — these tests cover the config-normalization layer
that prevents that from happening by accident via docker-compose's
`${QDRANT_API_KEY:-}` substitution."""

import pytest

from app.core.config import Settings
from app.services.guidance_retrieval import GuidanceService, check_qdrant_reachable


def test_empty_string_qdrant_api_key_normalizes_to_none(monkeypatch):
    monkeypatch.setenv("PART2_QDRANT_API_KEY", "")
    settings = Settings()
    assert settings.qdrant_api_key is None


def test_unset_qdrant_api_key_is_none(monkeypatch):
    monkeypatch.delenv("PART2_QDRANT_API_KEY", raising=False)
    settings = Settings()
    assert settings.qdrant_api_key is None


def test_real_qdrant_api_key_is_preserved(monkeypatch):
    monkeypatch.setenv("PART2_QDRANT_API_KEY", "a-real-key")
    settings = Settings()
    assert settings.qdrant_api_key == "a-real-key"


class _RecordingQdrantClient:
    """Records the api_key it was constructed with, without making any
    network call — used to prove the key is actually threaded through to
    the qdrant-client constructor at every call site."""

    last_api_key: str | None = "unset"

    def __init__(self, url, api_key=None, timeout=None):
        _RecordingQdrantClient.last_api_key = api_key

    async def get_collections(self):
        return None

    async def close(self):
        pass


@pytest.mark.asyncio
async def test_guidance_service_passes_configured_api_key(monkeypatch):
    import app.services.guidance_retrieval as guidance_retrieval_module

    monkeypatch.setattr(guidance_retrieval_module, "AsyncQdrantClient", _RecordingQdrantClient)
    settings = Settings(qdrant_api_key="secret-123")

    service = GuidanceService(settings)
    service._get_client()

    assert _RecordingQdrantClient.last_api_key == "secret-123"


@pytest.mark.asyncio
async def test_guidance_service_passes_none_when_unconfigured(monkeypatch):
    import app.services.guidance_retrieval as guidance_retrieval_module

    monkeypatch.setattr(guidance_retrieval_module, "AsyncQdrantClient", _RecordingQdrantClient)
    settings = Settings(qdrant_api_key=None)

    service = GuidanceService(settings)
    service._get_client()

    assert _RecordingQdrantClient.last_api_key is None


@pytest.mark.asyncio
async def test_health_check_passes_configured_api_key(monkeypatch):
    import app.services.guidance_retrieval as guidance_retrieval_module

    monkeypatch.setattr(guidance_retrieval_module, "AsyncQdrantClient", _RecordingQdrantClient)
    settings = Settings(qdrant_api_key="secret-456")

    await check_qdrant_reachable(settings)

    assert _RecordingQdrantClient.last_api_key == "secret-456"

import pytest

from app.api import routes_health

pytestmark = pytest.mark.asyncio


async def test_live(client):
    resp = await client.get("/api/v1/health/live")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


async def test_ready(client):
    resp = await client.get("/api/v1/health/ready")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["dependencies"]["database"] is True


async def test_ready_reports_vector_store_not_configured_without_qdrant(client):
    # No Qdrant reachable in the test environment (default profile has none):
    # honest "not_configured", and overall readiness is NOT blocked by it —
    # retrieval is supplemental-only, per ADR-004/D-09.
    resp = await client.get("/api/v1/health/ready")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["dependencies"]["vector_store"] == "not_configured"


async def test_ready_reports_vector_store_qdrant_when_reachable(client, monkeypatch):
    async def _fake_reachable(settings, timeout_s=None):
        return True

    monkeypatch.setattr(routes_health, "check_qdrant_reachable", _fake_reachable)

    resp = await client.get("/api/v1/health/ready")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["dependencies"]["vector_store"] == "qdrant"


async def test_config(client):
    resp = await client.get("/api/v1/config")
    assert resp.status_code == 200
    body = resp.json()
    assert body["deployment_mode"] == "local"
    assert "has_credential" in body
    assert "credential" not in body


async def test_config_test_reports_provider_unavailable_without_ollama(client):
    # No Ollama reachable in the test environment: honest failure, not a faked success.
    resp = await client.post("/api/v1/config/test")
    assert resp.status_code == 503
    assert resp.json()["error"]["code"] == "PROVIDER_UNAVAILABLE"


async def test_list_providers_shows_full_catalog_with_implemented_flags(client):
    resp = await client.get("/api/v1/config/providers")
    assert resp.status_code == 200
    body = resp.json()
    by_type = {p["provider_type"]: p["implemented"] for p in body}
    assert by_type == {
        "ollama": True,
        "anthropic": False,
        "openai": False,
        "gemini": False,
    }


async def test_update_config_saves_ollama_provider_and_model(client):
    resp = await client.put("/api/v1/config", json={"provider_type": "ollama", "model_name": "qwen3:4b"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["provider_type"] == "ollama"
    assert body["model_name"] == "qwen3:4b"


async def test_update_config_rejects_unimplemented_provider(client):
    resp = await client.put("/api/v1/config", json={"provider_type": "anthropic"})
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "CONFIGURATION_INVALID"
    # Rejected outright: GET must show the config unchanged, not partially applied.
    get_resp = await client.get("/api/v1/config")
    assert get_resp.json()["provider_type"] != "anthropic"


async def test_update_config_rejects_unknown_provider(client):
    resp = await client.put("/api/v1/config", json={"provider_type": "not-a-real-provider"})
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "CONFIGURATION_INVALID"


async def test_update_config_rejects_base_url_for_non_ollama_provider(client, monkeypatch):
    # Since only `ollama` can ever be saved via PUT (_SAVEABLE_PROVIDERS), the
    # only way the *effective* provider is non-ollama is Settings.provider_type
    # itself being non-ollama (an env-configured deployment default) — not
    # reachable purely through PUT requests in the default test environment.
    # Simulate that deployment shape directly to exercise the check.
    from app.api import routes_config
    from app.core.config import Settings

    class _AnthropicDefaultSettings(Settings):
        provider_type: str = "anthropic"

    monkeypatch.setattr(routes_config, "get_settings", lambda: _AnthropicDefaultSettings())

    resp = await client.put("/api/v1/config", json={"base_url": "http://example.com:11434"})
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "CONFIGURATION_INVALID"


async def test_update_config_rejects_invalid_ollama_base_url(client):
    resp = await client.put(
        "/api/v1/config",
        json={"provider_type": "ollama", "base_url": "not-a-valid-url"},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "CONFIGURATION_INVALID"
    # Rejected outright: GET must show the base URL unchanged.
    get_resp = await client.get("/api/v1/config")
    assert get_resp.json()["base_url_display"] != "not-a-valid-url"


async def test_update_config_accepts_valid_ollama_base_url(client):
    resp = await client.put(
        "/api/v1/config",
        json={"provider_type": "ollama", "base_url": "http://ollama:11434"},
    )
    assert resp.status_code == 200
    assert resp.json()["base_url_display"] == "http://ollama:11434"


async def test_update_config_rejects_javascript_scheme_base_url(client):
    resp = await client.put(
        "/api/v1/config",
        json={"provider_type": "ollama", "base_url": "javascript:alert(1)"},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "CONFIGURATION_INVALID"


async def test_update_config_never_returns_credential_value(client):
    resp = await client.put("/api/v1/config", json={"credential": "super-secret-value"})
    assert resp.status_code == 200
    body = resp.json()
    assert "credential" not in body
    assert "super-secret-value" not in resp.text
    assert body["has_credential"] is True


async def test_update_config_rejected_unconditionally_in_demo_mode(client, monkeypatch):
    # P7: backend-enforced lock, not just a hidden admin nav link — the
    # hosted demo is deterministic-only and must reject config writes even
    # from a client that reaches the API directly. Demo access credentials
    # are also configured here so this test exercises the config lock
    # itself, not the separate DemoBasicAuthMiddleware gate (see
    # test_demo_access.py).
    import base64

    from app.core.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "deployment_mode", "demo")
    monkeypatch.setattr(settings, "demo_access_username", "demo-user")
    monkeypatch.setattr(settings, "demo_access_password", "demo-pass")
    token = base64.b64encode(b"demo-user:demo-pass").decode()
    auth_headers = {"Authorization": f"Basic {token}"}

    resp = await client.put(
        "/api/v1/config",
        json={"provider_type": "ollama", "model_name": "qwen3:4b"},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "CONFIGURATION_INVALID"

    # Even a no-op-looking payload is rejected, not silently accepted.
    resp2 = await client.put("/api/v1/config", json={}, headers=auth_headers)
    assert resp2.status_code == 400

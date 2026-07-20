"""Hosted-demo access control evidence (P7): DemoBasicAuthMiddleware gates
every request when Settings.deployment_mode == "demo", is a no-op in
"local" mode, and fails closed if demo mode is active without configured
credentials. See docs/SECURITY_EVIDENCE.md section 10."""

import base64

import pytest

from app.core.config import get_settings

pytestmark = pytest.mark.asyncio


def _basic_auth_header(username: str, password: str) -> dict[str, str]:
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


async def test_local_mode_requires_no_auth(client):
    resp = await client.get("/api/v1/config")
    assert resp.status_code == 200


async def test_demo_mode_without_credentials_fails_closed(client, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "deployment_mode", "demo")
    monkeypatch.setattr(settings, "demo_access_username", None)
    monkeypatch.setattr(settings, "demo_access_password", None)

    resp = await client.get("/api/v1/config")
    assert resp.status_code == 503


async def test_demo_mode_rejects_missing_credentials(client, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "deployment_mode", "demo")
    monkeypatch.setattr(settings, "demo_access_username", "demo-user")
    monkeypatch.setattr(settings, "demo_access_password", "demo-pass")

    resp = await client.get("/api/v1/config")
    assert resp.status_code == 401
    assert resp.headers.get("www-authenticate", "").lower().startswith("basic")


async def test_demo_mode_rejects_wrong_credentials(client, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "deployment_mode", "demo")
    monkeypatch.setattr(settings, "demo_access_username", "demo-user")
    monkeypatch.setattr(settings, "demo_access_password", "demo-pass")

    resp = await client.get("/api/v1/config", headers=_basic_auth_header("demo-user", "wrong"))
    assert resp.status_code == 401


async def test_demo_mode_accepts_correct_credentials(client, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "deployment_mode", "demo")
    monkeypatch.setattr(settings, "demo_access_username", "demo-user")
    monkeypatch.setattr(settings, "demo_access_password", "demo-pass")

    resp = await client.get("/api/v1/config", headers=_basic_auth_header("demo-user", "demo-pass"))
    assert resp.status_code == 200


async def test_health_live_exempt_from_demo_auth(client, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "deployment_mode", "demo")
    monkeypatch.setattr(settings, "demo_access_username", "demo-user")
    monkeypatch.setattr(settings, "demo_access_password", "demo-pass")

    resp = await client.get("/api/v1/health/live")
    assert resp.status_code == 200

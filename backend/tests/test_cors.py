"""CORS restriction evidence (P6) — Settings.cors_allow_origins is already
enforced by CORSMiddleware in main.py (unchanged since P0); this test just
proves an unlisted origin gets no Access-Control-Allow-Origin header, and an
allowed one does."""

import pytest

pytestmark = pytest.mark.asyncio


async def test_disallowed_origin_gets_no_cors_header(client):
    resp = await client.get(
        "/api/v1/health/live",
        headers={"Origin": "https://evil.example.com"},
    )
    assert resp.status_code == 200
    assert "access-control-allow-origin" not in resp.headers


async def test_allowed_origin_gets_cors_header(client):
    resp = await client.get(
        "/api/v1/health/live",
        headers={"Origin": "http://localhost:5173"},
    )
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"

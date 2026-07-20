"""Retention enforcement tests (P6).

Lazy delete-on-read only — there is no background sweep. This is
deliberately PoC-scale retention (see SECURITY_AND_DATA.md's "PoC
retention, not production archival" note), not a production records
archival policy: an unread expired review simply stays in SQLite
indefinitely until the next GET for it."""

import asyncio
import os
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from app.core.config import get_settings
from app.db.models import Review
from app.db.session import async_session_factory

pytestmark = pytest.mark.asyncio

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "fixtures")


async def _create_and_complete_review(client) -> str:
    with open(os.path.join(FIXTURES_DIR, "sentinel-support-agreement.pdf"), "rb") as f:
        content = f.read()
    resp = await client.post(
        "/api/v1/reviews", files={"file": ("sentinel-support-agreement.pdf", content, "application/pdf")}
    )
    review_id = resp.json()["review_id"]
    for _ in range(50):
        status_resp = await client.get(f"/api/v1/reviews/{review_id}")
        if status_resp.json()["status"] in ("completed", "failed"):
            break
        await asyncio.sleep(0.1)
    return review_id


async def _age_review(review_id: str, hours: float) -> None:
    async with async_session_factory() as session:
        result = await session.execute(select(Review).where(Review.id == review_id))
        review = result.scalar_one()
        review.completed_at = datetime.now(timezone.utc) - timedelta(hours=hours)
        await session.commit()


async def test_fresh_review_is_not_expired(client):
    review_id = await _create_and_complete_review(client)
    resp = await client.get(f"/api/v1/reviews/{review_id}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"


async def test_review_past_local_retention_window_returns_expired_and_is_deleted(client):
    review_id = await _create_and_complete_review(client)
    settings = get_settings()
    await _age_review(review_id, hours=settings.retention_hours_local + 1)

    resp = await client.get(f"/api/v1/reviews/{review_id}")
    assert resp.status_code == 410
    assert resp.json()["error"]["code"] == "REVIEW_EXPIRED"

    # Lazily deleted on that read — a second GET is a plain 404, not another
    # 410, proving the row is actually gone rather than re-evaluated.
    second_resp = await client.get(f"/api/v1/reviews/{review_id}")
    assert second_resp.status_code == 404
    assert second_resp.json()["error"]["code"] == "REVIEW_NOT_FOUND"


async def test_review_within_retention_window_is_not_expired(client):
    review_id = await _create_and_complete_review(client)
    settings = get_settings()
    await _age_review(review_id, hours=settings.retention_hours_local - 1)

    resp = await client.get(f"/api/v1/reviews/{review_id}")
    assert resp.status_code == 200


async def test_demo_mode_uses_shorter_retention_window(client, monkeypatch):
    review_id = await _create_and_complete_review(client)

    async with async_session_factory() as session:
        result = await session.execute(select(Review).where(Review.id == review_id))
        review = result.scalar_one()
        review.deployment_mode = "demo"
        await session.commit()

    settings = get_settings()
    # Past the (shorter) demo window but within the local one — proves the
    # per-review deployment_mode drives which retention window applies, not
    # a single global setting.
    assert settings.retention_hours_demo < settings.retention_hours_local
    await _age_review(review_id, hours=settings.retention_hours_demo + 1)

    resp = await client.get(f"/api/v1/reviews/{review_id}")
    assert resp.status_code == 410
    assert resp.json()["error"]["code"] == "REVIEW_EXPIRED"


async def test_in_progress_review_is_never_expired_regardless_of_created_at_age(client):
    # An active (non-terminal) review has no completed_at yet — retention
    # must never touch it no matter how old created_at is.
    with open(os.path.join(FIXTURES_DIR, "sentinel-support-agreement.pdf"), "rb") as f:
        content = f.read()
    resp = await client.post(
        "/api/v1/reviews", files={"file": ("sentinel-support-agreement.pdf", content, "application/pdf")}
    )
    review_id = resp.json()["review_id"]

    async with async_session_factory() as session:
        result = await session.execute(select(Review).where(Review.id == review_id))
        review = result.scalar_one()
        review.created_at = datetime.now(timezone.utc) - timedelta(days=365)
        await session.commit()

    status_resp = await client.get(f"/api/v1/reviews/{review_id}")
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] in ("queued", "parsing", "analyzing", "validating", "completed")

    # Drain the background job so it doesn't get torn down mid-flight when
    # the test's event loop closes (pure test hygiene, not part of the
    # assertion above).
    for _ in range(50):
        drain_resp = await client.get(f"/api/v1/reviews/{review_id}")
        if drain_resp.json()["status"] in ("completed", "failed"):
            break
        await asyncio.sleep(0.1)

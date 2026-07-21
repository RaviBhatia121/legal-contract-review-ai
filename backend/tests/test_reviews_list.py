"""GET /api/v1/reviews — summary-list endpoint for the dashboard (P8.1).

Summary-only: never evidence_text, full findings, parsed_text, or
model/credential internals. Retention-aware: expired terminal reviews
encountered on a page are deleted, same lazy delete-on-read behavior as
GET /{review_id} — so a returned page may contain fewer than `limit` items
when expired rows were purged (documented behavior, not a bug)."""

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


async def test_empty_list(client):
    resp = await client.get("/api/v1/reviews")
    assert resp.status_code == 200
    assert resp.json() == {"items": [], "limit": 20, "offset": 0}


async def test_ordering_is_newest_first(client):
    first_id = await _create_and_complete_review(client)
    second_id = await _create_and_complete_review(client)

    resp = await client.get("/api/v1/reviews")
    assert resp.status_code == 200
    ids = [item["review_id"] for item in resp.json()["items"]]
    assert ids.index(second_id) < ids.index(first_id)


async def test_limit_and_offset_respected(client):
    for _ in range(3):
        await _create_and_complete_review(client)

    resp = await client.get("/api/v1/reviews", params={"limit": 2, "offset": 0})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["items"]) == 2
    assert body["limit"] == 2
    assert body["offset"] == 0

    resp2 = await client.get("/api/v1/reviews", params={"limit": 2, "offset": 2})
    assert len(resp2.json()["items"]) == 1


async def test_limit_over_max_is_rejected(client):
    resp = await client.get("/api/v1/reviews", params={"limit": 51})
    assert resp.status_code == 422


async def test_aggregate_counts_match_single_review_endpoint(client):
    review_id = await _create_and_complete_review(client)

    single = await client.get(f"/api/v1/reviews/{review_id}")
    single_summary = single.json()["review_summary"]

    listed = await client.get("/api/v1/reviews")
    item = next(i for i in listed.json()["items"] if i["review_id"] == review_id)

    assert item["findings_total"] == single_summary["findings_total"]
    assert item["missing_clause_count"] == single_summary["missing_clause_count"]
    assert item["needs_review_count"] == single_summary["needs_review_count"]
    assert item["overall_risk"] == single_summary["overall_risk"]


async def test_non_completed_review_has_zeroed_counts(client):
    with open(os.path.join(FIXTURES_DIR, "sentinel-support-agreement.pdf"), "rb") as f:
        content = f.read()
    create_resp = await client.post(
        "/api/v1/reviews", files={"file": ("sentinel-support-agreement.pdf", content, "application/pdf")}
    )
    review_id = create_resp.json()["review_id"]

    listed = await client.get("/api/v1/reviews")
    item = next(i for i in listed.json()["items"] if i["review_id"] == review_id)
    assert item["overall_risk"] is None
    assert item["completed_at"] is None
    assert item["findings_total"] == 0
    assert item["missing_clause_count"] == 0
    assert item["needs_review_count"] == 0

    # Drain so the background job doesn't get torn down mid-flight.
    for _ in range(50):
        drain_resp = await client.get(f"/api/v1/reviews/{review_id}")
        if drain_resp.json()["status"] in ("completed", "failed"):
            break
        await asyncio.sleep(0.1)


async def test_expired_review_is_absent_and_deleted(client):
    review_id = await _create_and_complete_review(client)
    settings = get_settings()
    await _age_review(review_id, hours=settings.retention_hours_local + 1)

    resp = await client.get("/api/v1/reviews")
    assert resp.status_code == 200
    ids = [item["review_id"] for item in resp.json()["items"]]
    assert review_id not in ids

    # Actually deleted by the list call, not just filtered — a direct GET
    # now returns 404 (row gone), not 410 (row present but expired).
    single = await client.get(f"/api/v1/reviews/{review_id}")
    assert single.status_code == 404
    assert single.json()["error"]["code"] == "REVIEW_NOT_FOUND"


async def test_payload_excludes_evidence_and_full_findings(client):
    await _create_and_complete_review(client)
    resp = await client.get("/api/v1/reviews")
    assert resp.status_code == 200
    raw_text = resp.text
    assert "evidence_text" not in raw_text
    assert "parsed_text" not in raw_text
    item = resp.json()["items"][0]
    assert "findings" not in item
    assert "missing_clauses" not in item


async def test_demo_mode_gates_list_endpoint(client, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "deployment_mode", "demo")
    monkeypatch.setattr(settings, "demo_access_username", "demo-user")
    monkeypatch.setattr(settings, "demo_access_password", "demo-pass")

    resp = await client.get("/api/v1/reviews")
    assert resp.status_code == 401

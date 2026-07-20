"""MaxBodySizeMiddleware tests (P6) — early rejection based on Content-Length,
distinct from and in addition to app.services.upload's post-read size check
(see test_reviews_golden_path.py::test_upload_rejects_oversized_file for
that one, which stays in place unchanged)."""

import pytest

pytestmark = pytest.mark.asyncio


async def test_oversized_content_length_rejected_before_body_processing(client):
    # Comfortably past the middleware's threshold (max_upload_bytes + 1MiB
    # overhead allowance = 16MiB here), so this proves the *early* ASGI-level
    # rejection path, not the post-read validate_and_read_upload() check.
    big_body = b"0" * (20 * 1024 * 1024)
    resp = await client.post(
        "/api/v1/reviews",
        content=big_body,
        headers={"Content-Type": "application/pdf"},
    )
    assert resp.status_code == 413
    assert resp.json()["error"]["code"] == "FILE_TOO_LARGE"


async def test_small_request_is_not_affected_by_body_size_middleware(client):
    # A trivially small request (well under the threshold) must pass through
    # untouched — confirms the middleware isn't overzealous.
    resp = await client.get("/api/v1/health/live")
    assert resp.status_code == 200

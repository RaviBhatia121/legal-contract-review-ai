"""Log-redaction evidence (P6): the job_runner's blanket exception handler
must never leak document content or credential-like strings into logs, even
when the failure carries them in its exception message (e.g. a
ValidationError echoing quoted evidence text)."""

import asyncio
import logging
import os

import pytest

from app.core import job_runner

pytestmark = pytest.mark.asyncio

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "fixtures")

_SENTINEL_SECRET = "sk-super-secret-credential-value-should-never-log"
_SENTINEL_EVIDENCE = "This is quoted contract evidence text that must not appear in logs."


async def test_unexpected_failure_logs_type_and_review_id_only(client, caplog, monkeypatch):
    def _boom(*args, **kwargs):
        raise RuntimeError(f"leaked secret={_SENTINEL_SECRET} evidence={_SENTINEL_EVIDENCE}")

    monkeypatch.setattr(job_runner, "evaluate_clauses", _boom)

    with open(os.path.join(FIXTURES_DIR, "sentinel-support-agreement.pdf"), "rb") as f:
        content = f.read()

    with caplog.at_level(logging.ERROR, logger="app.core.job_runner"):
        resp = await client.post(
            "/api/v1/reviews", files={"file": ("sentinel-support-agreement.pdf", content, "application/pdf")}
        )
        review_id = resp.json()["review_id"]

        for _ in range(50):
            status_resp = await client.get(f"/api/v1/reviews/{review_id}")
            if status_resp.json()["status"] in ("completed", "failed"):
                break
            await asyncio.sleep(0.1)

    assert status_resp.json()["status"] == "failed"
    assert status_resp.json()["error"]["code"] == "INTERNAL_ERROR"
    # The API's own error message is the fixed safe string, never the raw exception.
    assert _SENTINEL_SECRET not in status_resp.text
    assert _SENTINEL_EVIDENCE not in status_resp.text

    # The captured application logs must not contain the secret/evidence
    # sentinels, only the safe type+review_id line.
    assert _SENTINEL_SECRET not in caplog.text
    assert _SENTINEL_EVIDENCE not in caplog.text
    assert "RuntimeError" in caplog.text
    assert review_id in caplog.text

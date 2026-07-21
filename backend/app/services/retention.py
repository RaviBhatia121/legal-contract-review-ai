"""PoC retention check (P6, extracted in P8.1 for reuse by list/single-review
routes). Lazy delete-on-read only — there is no background sweep (see
SECURITY_AND_DATA.md's "PoC retention, not production archival" note)."""

from datetime import datetime, timezone

from app.core.config import Settings
from app.db.models import Review

TERMINAL_STATUSES = ("completed", "failed")


def retention_hours_for(review: Review, settings: Settings) -> float:
    return settings.retention_hours_demo if review.deployment_mode == "demo" else settings.retention_hours_local


def is_expired(review: Review, settings: Settings) -> bool:
    """Only applies to terminal reviews with a completed_at timestamp; an
    in-progress review is never expired regardless of how old its
    `created_at` is."""
    if review.status not in TERMINAL_STATUSES or review.completed_at is None:
        return False
    # SQLite drops tzinfo on round-trip even though the column is declared
    # DateTime(timezone=True); values are always written as UTC (see
    # db/models.py's _now()), so a naive read-back is safely treated as UTC.
    completed_at = review.completed_at
    if completed_at.tzinfo is None:
        completed_at = completed_at.replace(tzinfo=timezone.utc)
    age_hours = (datetime.now(timezone.utc) - completed_at).total_seconds() / 3600
    return age_hours > retention_hours_for(review, settings)

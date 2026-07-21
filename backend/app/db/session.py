from collections.abc import AsyncIterator

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.db.models import Base

_settings = get_settings()
engine = create_async_engine(_settings.database_url, echo=False)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_ensure_review_provenance_columns)


def _ensure_review_provenance_columns(sync_conn) -> None:
    """Prototype-safe additive schema update for existing local SQLite DBs."""
    columns = {column["name"] for column in inspect(sync_conn).get_columns("reviews")}
    additions = {
        "mode_requested": "ALTER TABLE reviews ADD COLUMN mode_requested VARCHAR(32) DEFAULT 'deterministic'",
        "mode_used": "ALTER TABLE reviews ADD COLUMN mode_used VARCHAR(32) DEFAULT 'deterministic'",
        "fallback_used": "ALTER TABLE reviews ADD COLUMN fallback_used BOOLEAN DEFAULT 0",
        "fallback_reason": "ALTER TABLE reviews ADD COLUMN fallback_reason VARCHAR(128)",
    }
    for column, statement in additions.items():
        if column not in columns:
            sync_conn.execute(text(statement))


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session_factory() as session:
        yield session

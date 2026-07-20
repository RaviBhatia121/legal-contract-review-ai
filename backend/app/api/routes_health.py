from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.core.config import get_settings
from app.db.session import get_session
from app.services.guidance_retrieval import check_qdrant_reachable

router = APIRouter(prefix="/api/v1/health", tags=["health"])


@router.get("/live")
async def live() -> dict:
    return {"status": "ok"}


@router.get("/ready")
async def ready(session: AsyncSession = Depends(get_session)) -> dict:
    database_ready = True
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        database_ready = False

    # P4: real reachability, not a hardcoded placeholder. Retrieval is
    # opt-in (the `retrieval` Compose profile) and supplemental-only, so an
    # unreachable/absent Qdrant is a safe "not_configured" — it never
    # affects overall readiness `status` or blocks the default deterministic
    # stack, which has no Qdrant to reach in the first place.
    vector_store = "qdrant" if await check_qdrant_reachable(get_settings()) else "not_configured"

    return {
        "status": "ok" if database_ready else "degraded",
        "dependencies": {
            "database": database_ready,
            "model_provider": "not_configured",
            "vector_store": vector_store,
        },
    }

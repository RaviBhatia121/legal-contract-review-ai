from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from app.api import routes_config, routes_health, routes_playbooks, routes_reviews
from app.core.config import get_settings
from app.core.job_runner import recover_interrupted_jobs
from app.core.middleware import DemoBasicAuthMiddleware, MaxBodySizeMiddleware
from app.db.session import init_db

# Multipart overhead (boundaries, field headers) on top of the actual file
# content limit enforced (authoritatively) in app.services.upload.
_BODY_SIZE_OVERHEAD_BYTES = 1_048_576

# P7: only present in the hosted image (backend/Dockerfile.hosted copies the
# built frontend `dist/` here). Absent in local dev and the default
# backend/Dockerfile, so the SPA fallback route below is a pure no-op for
# every non-hosted deployment.
_FRONTEND_DIST = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await recover_interrupted_jobs()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Part 2 Legal Contract Risk Review API", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        MaxBodySizeMiddleware,
        max_body_bytes=settings.max_upload_bytes + _BODY_SIZE_OVERHEAD_BYTES,
    )
    # P7: outermost middleware (added last => runs first) so hosted-demo
    # access control gates every request, including CORS preflights and
    # oversized-body rejections. No-op unless deployment_mode == "demo".
    app.add_middleware(DemoBasicAuthMiddleware)

    app.include_router(routes_health.router)
    app.include_router(routes_config.router)
    app.include_router(routes_playbooks.router)
    app.include_router(routes_reviews.router)

    # P7: serve the built frontend same-origin from the backend in the
    # hosted image only (see _FRONTEND_DIST above). Registered after the API
    # routers so `/api/v1/...` always resolves there first; this catch-all
    # only ever matches non-API paths. Falls back to `index.html` for any
    # path that isn't a real static asset, so client-side (react-router)
    # routes resolve correctly on a hard refresh (e.g. `/reviews/<id>`).
    if _FRONTEND_DIST.is_dir():

        @app.get("/{full_path:path}", include_in_schema=False)
        async def serve_frontend(full_path: str) -> FileResponse:
            candidate = _FRONTEND_DIST / full_path
            if full_path and candidate.is_file():
                return FileResponse(candidate)
            return FileResponse(_FRONTEND_DIST / "index.html")

    @app.exception_handler(FastAPIHTTPException)
    async def api_error_handler(request: Request, exc: FastAPIHTTPException) -> JSONResponse:
        body = exc.detail if isinstance(exc.detail, dict) and "error" in exc.detail else {
            "error": {"code": "INTERNAL_ERROR", "message": str(exc.detail), "retryable": False}
        }
        return JSONResponse(status_code=exc.status_code, content=body)

    return app


app = create_app()

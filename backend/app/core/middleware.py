"""Early request-body size rejection (P6) and hosted-demo access gate (P7).

Defense in depth, NOT the only protection: `MaxBodySizeMiddleware` rejects
requests whose client-supplied `Content-Length` header already exceeds the
limit, before Starlette/FastAPI buffers the body into memory — closing the
gap where `app.services.upload.validate_and_read_upload`'s size check only
runs *after* `await file.read()` has already read the full body. A client
can omit or lie about `Content-Length`, so that post-read check in
`upload.py` remains the authoritative guard and must not be removed.
"""

import base64
import secrets

from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.config import get_settings


class MaxBodySizeMiddleware:
    def __init__(self, app: ASGIApp, max_body_bytes: int):
        self.app = app
        self.max_body_bytes = max_body_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers") or [])
        raw_length = headers.get(b"content-length")
        if raw_length is not None:
            try:
                length = int(raw_length)
            except ValueError:
                length = None
            if length is not None and length > self.max_body_bytes:
                response = JSONResponse(
                    status_code=413,
                    content={
                        "error": {
                            "code": "FILE_TOO_LARGE",
                            "message": "The request body exceeds the maximum allowed size.",
                            "retryable": False,
                        }
                    },
                )
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)


# P7: liveness must stay reachable without credentials so the hosting
# platform's own process/port check (not an app-level concern) never depends
# on demo access credentials being configured correctly.
_AUTH_EXEMPT_PATHS = {"/api/v1/health/live"}


class DemoBasicAuthMiddleware:
    """Gate every request behind HTTP Basic Auth when deployment_mode is
    "demo" (P7 hosted-demo access control, D-06). No-op in "local" mode.
    Checks Settings.deployment_mode/demo_access_username/demo_access_password
    fresh on every request (not baked in at app construction) so it reacts to
    the actual runtime configuration, matching the rest of the security
    middleware in this module.

    Fails closed: if demo mode is active but no credentials are configured,
    every request is rejected rather than served unauthenticated — a hosted
    deployment with demo mode on and no access credentials set is a
    misconfiguration, not a valid "no auth needed" state.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        settings = get_settings()
        if settings.deployment_mode != "demo" or scope.get("path") in _AUTH_EXEMPT_PATHS:
            await self.app(scope, receive, send)
            return

        expected_user = settings.demo_access_username
        expected_pass = settings.demo_access_password
        if not expected_user or not expected_pass:
            response = JSONResponse(
                status_code=503,
                content={
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "Hosted demo access is not configured.",
                        "retryable": False,
                    }
                },
            )
            await response(scope, receive, send)
            return

        headers = dict(scope.get("headers") or [])
        auth_header = headers.get(b"authorization")
        if auth_header and _is_valid_basic_auth(auth_header, expected_user, expected_pass):
            await self.app(scope, receive, send)
            return

        response = Response(status_code=401, headers={"WWW-Authenticate": 'Basic realm="demo"'})
        await response(scope, receive, send)


def _is_valid_basic_auth(header_value: bytes, expected_user: str, expected_pass: str) -> bool:
    try:
        scheme, _, encoded = header_value.decode("latin-1").partition(" ")
        if scheme.lower() != "basic":
            return False
        decoded = base64.b64decode(encoded).decode("utf-8")
        username, _, password = decoded.partition(":")
    except Exception:
        return False
    return secrets.compare_digest(username, expected_user) and secrets.compare_digest(password, expected_pass)

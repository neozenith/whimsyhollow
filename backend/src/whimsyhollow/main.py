"""FastAPI application factory + entrypoint.

Run locally:  uv run uvicorn whimsyhollow.main:app --reload
In container:  uvicorn whimsyhollow.main:app --host 0.0.0.0 --port $PORT
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api.auth import iap_email
from .api.routes import health
from .config import Settings, get_settings
from .identity import mask_user_id
from .logging_setup import configure_logging


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title="whimsyhollow",
        version="0.1.0",
        summary="Minimal async FastAPI backend: tiny JSON API + React SPA serving.",
        servers=[{"url": "/", "description": settings.environment}],
    )

    # Backend API surface, all under /api.
    app.include_router(health.router, prefix="/api")

    @app.get("/api/me", tags=["identity"])
    async def me(request: Request) -> dict[str, Any]:
        """Identity the SPA shows — from the IAP header in prod, null when no header.

        `user_id` is a pseudonymous, server-derived id; the raw email is never used as a
        key downstream. No RBAC in this plain version, so every caller is a plain user."""
        email = iap_email(request)
        return {
            "email": email,
            "user_id": mask_user_id(email) if email else None,
            "environment": settings.environment,
            "roles": ["user"],
        }

    _mount_frontend(app, settings)
    return app


def _mount_frontend(app: FastAPI, settings: Settings) -> None:
    """Serve the built React SPA (static assets + client-side-routing fallback) when the
    dist directory exists. Registered last so /api routes win. When dist is absent (local
    dev where Vite serves the UI via proxy) the app still starts and serves the API — this
    is environment handling, not a skipped requirement."""
    dist = settings.static_dir
    index = dist / "index.html"
    if not index.exists():
        return

    assets = dist / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/{full_path:path}", response_class=FileResponse)
    async def spa(full_path: str) -> FileResponse:  # noqa: ARG001 — SPA client-side routing
        return FileResponse(index)


app = create_app()

"""Health check. NB: use /health, not /healthz — Google's frontend reserves /healthz
on Cloud Run and 404s it before it reaches the container."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

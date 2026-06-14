"""SPA serving: API works without a dist dir, and the catch-all serves index.html when
a dist dir exists. Real files in a tmp dir — no mocks."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from whimsyhollow.config import Settings
from whimsyhollow.main import create_app


def test_api_works_without_dist(tmp_path: Path) -> None:
    """No dist dir → API still serves; the SPA catch-all is simply not registered."""
    settings = Settings(static_dir=tmp_path / "does-not-exist")
    client = TestClient(create_app(settings))
    assert client.get("/api/health").json() == {"status": "ok"}


def test_spa_served_when_dist_exists(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("<!doctype html><title>whimsyhollow</title>", encoding="utf-8")
    (dist / "assets" / "app.js").write_text("console.log('hi')", encoding="utf-8")

    client = TestClient(create_app(Settings(static_dir=dist)))

    # API still wins.
    assert client.get("/api/health").json() == {"status": "ok"}
    # Client-side route falls back to index.html.
    spa = client.get("/some/client/route")
    assert spa.status_code == 200
    assert "whimsyhollow" in spa.text
    # Static asset is served.
    asset = client.get("/assets/app.js")
    assert asset.status_code == 200
    assert "console.log" in asset.text

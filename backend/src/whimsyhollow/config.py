"""Central settings (the env-var registry for the backend). Everything reads from
here via get_settings(); nothing reads os.environ directly. Kept deliberately minimal."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_static_dir() -> Path:
    """The built React SPA dir, resolved relative to this package's repo root.

    config.py lives at backend/src/whimsyhollow/config.py, so parents[3] is the repo
    root (whimsyhollow/), giving whimsyhollow/frontend/dist. Overridable via STATIC_DIR
    (the container sets it to /app/frontend_dist)."""
    return Path(__file__).resolve().parents[3] / "frontend" / "dist"


class Settings(BaseSettings):
    """Backend configuration. Pulled from environment / .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "local"
    log_level: str = "INFO"
    port: int = 8080

    # Built React SPA dir served by FastAPI. Absent on a local backend-only run (Vite
    # serves the UI via proxy) → SPA disabled, API still serves.
    static_dir: Path = Field(default_factory=_default_static_dir)


@lru_cache
def get_settings() -> Settings:
    """Singleton settings. lru_cache so every caller shares one instance."""
    return Settings()

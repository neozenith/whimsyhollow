"""Shared fixtures. Real FastAPI TestClient only — no mocks (project rule)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from whimsyhollow.main import create_app


@pytest.fixture
def client() -> TestClient:
    """A TestClient backed by the default app (default settings → no SPA dist present)."""
    return TestClient(create_app())

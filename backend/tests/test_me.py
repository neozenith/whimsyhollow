"""GET /api/me identity contract."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_me_no_header(client: TestClient) -> None:
    resp = client.get("/api/me")
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] is None
    assert body["user_id"] is None
    assert body["environment"] == "local"
    assert body["roles"] == ["user"]


def test_me_iap_prefixed_header(client: TestClient) -> None:
    resp = client.get(
        "/api/me",
        headers={"X-Goog-Authenticated-User-Email": "accounts.google.com:alice@example.com"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "alice@example.com"
    assert body["user_id"]  # non-null, stable id
    assert body["roles"] == ["user"]


def test_me_plain_email_header(client: TestClient) -> None:
    resp = client.get(
        "/api/me",
        headers={"X-Goog-Authenticated-User-Email": "bob@example.com"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == "bob@example.com"
    assert body["user_id"]


def test_me_user_id_matches_prefixed_and_plain(client: TestClient) -> None:
    """Same identity via prefixed or plain header yields the same user_id."""
    prefixed = client.get(
        "/api/me",
        headers={"X-Goog-Authenticated-User-Email": "accounts.google.com:carol@example.com"},
    ).json()
    plain = client.get(
        "/api/me",
        headers={"X-Goog-Authenticated-User-Email": "carol@example.com"},
    ).json()
    assert prefixed["user_id"] == plain["user_id"]

"""Unit tests for the pure identity helpers (no framework, no mocks)."""

from __future__ import annotations

from whimsyhollow.identity import email_from_iap_header, mask_user_id


def test_prefixed_form() -> None:
    assert email_from_iap_header("accounts.google.com:alice@example.com") == "alice@example.com"


def test_plain_form() -> None:
    assert email_from_iap_header("bob@example.com") == "bob@example.com"


def test_empty_and_none() -> None:
    assert email_from_iap_header(None) is None
    assert email_from_iap_header("") is None
    assert email_from_iap_header("   ") is None
    assert email_from_iap_header("accounts.google.com:") is None


def test_mask_user_id_deterministic_and_normalised() -> None:
    assert mask_user_id("alice@example.com") == mask_user_id("  Alice@Example.com  ")


def test_mask_user_id_differs_and_opaque() -> None:
    masked = mask_user_id("alice@example.com")
    assert mask_user_id("alice@example.com") != mask_user_id("bob@example.com")
    assert "alice" not in masked
    assert len(masked) == 16

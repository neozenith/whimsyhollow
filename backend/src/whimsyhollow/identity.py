"""Request identity helpers — pure functions, no framework dependency.

`email_from_iap_header` parses the caller email out of the IAP header value (which
looks like ``accounts.google.com:user@example.com`` in prod, or a plain email when
simulated). `mask_user_id` derives a stable, opaque id from that email so the raw
address never becomes a downstream key.
"""

from __future__ import annotations

import hashlib


def email_from_iap_header(raw: str | None) -> str | None:
    """Extract the email from an IAP ``X-Goog-Authenticated-User-Email`` value.

    Handles the ``accounts.google.com:<email>`` prefixed form and the plain-email form;
    returns None for a missing or empty value."""
    if not raw:
        return None
    email = raw.split(":", 1)[-1].strip()
    return email or None


def mask_user_id(email: str) -> str:
    """Deterministic, opaque user id for an email — a short sha256 hex of the normalised
    (lowercased, trimmed) address, so the same identity always yields the same id."""
    return hashlib.sha256(email.strip().lower().encode("utf-8")).hexdigest()[:16]

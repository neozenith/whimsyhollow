"""Request identity from the IAP header.

`iap_email` reads the caller from the ``X-Goog-Authenticated-User-Email`` header (set by
IAP in prod; simulated by a client in non-prod). Parsing lives in identity.py."""

from __future__ import annotations

from fastapi import Request

from ..identity import email_from_iap_header

IAP_USER_HEADER = "x-goog-authenticated-user-email"


def iap_email(request: Request) -> str | None:
    """The caller's IAP email, or None when the header is absent/empty."""
    return email_from_iap_header(request.headers.get(IAP_USER_HEADER))

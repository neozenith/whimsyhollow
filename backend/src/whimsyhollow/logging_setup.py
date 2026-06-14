"""Logging configuration. Single-line, Cloud Logging friendly. Call configure_logging()
once at startup."""

from __future__ import annotations

import logging
import sys

_DETAILED = "%(asctime)s %(levelname)s %(name)s:%(lineno)d %(message)s"


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(_DETAILED))
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level.upper())
    # Quiet the noisy urllib3 transport logger unless we're debugging.
    logging.getLogger("urllib3").setLevel(max(logging.INFO, root.level))

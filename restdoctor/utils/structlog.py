from __future__ import annotations

try:
    from structlog import get_logger
except ImportError:
    from logging import getLogger as get_logger  # noqa: F401

try:
    from structlog.contextvars import bind_contextvars  # noqa: F401
except ImportError:
    bind_contextvars = None

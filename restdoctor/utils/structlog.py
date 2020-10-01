try:
    from structlog import get_logger
except ImportError:
    from logging import getLogger as get_logger  # noqa: F401

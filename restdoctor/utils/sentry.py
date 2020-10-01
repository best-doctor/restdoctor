try:
    from sentry_sdk import capture_exception
except ImportError:
    def capture_exception() -> None:
        pass

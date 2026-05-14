from __future__ import annotations

import importlib
import typing
from contextlib import contextmanager


@contextmanager
def internal_span(
    *, module: str, view_name: str, action: str
) -> typing.Generator[typing.Any, None, None]:
    trace: typing.Any = importlib.import_module('opentelemetry.trace')

    tracer = trace.get_tracer(module)
    name = f'{view_name}.{action}'
    with tracer.start_as_current_span(name, kind=trace.SpanKind.INTERNAL) as span:
        span.set_attribute('action', action)
        yield span

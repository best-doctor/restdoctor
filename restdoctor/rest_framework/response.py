from __future__ import annotations
import typing

from rest_framework.response import Response


class ResponseWithMeta(Response):
    def __init__(
        self, data: typing.Any, meta: typing.Dict[str, typing.Any] = None,
        *args: typing.Any, **kwargs: typing.Any,
    ) -> None:
        self.meta = meta
        super().__init__(data, *args, **kwargs)

    @property
    def rendered_content(self) -> bytes:
        context = getattr(self, 'renderer_context', None)
        if context:
            context['meta'] = self.meta

        return super().rendered_content

    def __getstate__(self) -> typing.Dict[str, typing.Any]:
        state = super().__getstate__()
        for key in (
            'meta',
        ):
            if key in state:
                del state[key]
        return state

from __future__ import annotations
import typing

from rest_framework.renderers import JSONRenderer

if typing.TYPE_CHECKING:
    from restdoctor.utils.custom_types import GenericContext
    from restdoctor.utils.media_type import APIParams


class RestDoctorRenderer(JSONRenderer):
    def __init__(self, media_type: str, api_params: typing.Optional[APIParams]) -> None:
        self.media_type = media_type
        self.api_params = api_params

    def render(
        self,
        data: GenericContext,
        accepted_media_type: str = None,
        renderer_context: typing.Optional[GenericContext] = None,
    ) -> bytes:
        renderer_context: GenericContext = renderer_context or {}
        if data is None or 'message' in data:
            result = data
        else:
            result = {'data': data}
            meta = renderer_context.get('meta')
            if meta:
                result['meta'] = meta

        verbose = bool(self.api_params and self.api_params.format.endswith('verbose'))
        if result is not None and verbose:
            result['query'] = {
                'args': renderer_context.get('args', []),
                **renderer_context.get('kwargs', {}),
            }

        return super().render(result, accepted_media_type, renderer_context)

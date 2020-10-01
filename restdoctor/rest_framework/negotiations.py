from __future__ import annotations
import typing

from rest_framework.negotiation import DefaultContentNegotiation

from restdoctor.rest_framework.parsers import BestDoctorParser
from restdoctor.utils.media_type import get_media_type
from restdoctor.rest_framework.renderers import RestDoctorRenderer

if typing.TYPE_CHECKING:
    from django.http import HttpRequest
    from restdoctor.rest_framework.custom_types import (
        Parsers, OptionalParser, OptionalRenderer, Renderers,
    )


class APIVersionContentNegotiation(DefaultContentNegotiation):
    def select_renderer(
        self, request: HttpRequest, renderers: Renderers, format_suffix: str,
    ) -> typing.Tuple[OptionalRenderer, str]:
        api_params = getattr(request, 'api_params', None)
        if api_params is not None:
            media_type = get_media_type(api_params)
            return RestDoctorRenderer(media_type, api_params), media_type

        return super().select_renderer(request, renderers, format_suffix)

    def select_parser(self, request: HttpRequest, parsers: Parsers) -> OptionalParser:
        api_params = getattr(request, 'api_params', None)
        parser = BestDoctorParser('application/json', api_params)

        return super().select_parser(request, [parser, *parsers])

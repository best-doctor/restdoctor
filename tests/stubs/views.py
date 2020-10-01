from __future__ import annotations
import typing

from rest_framework.response import Response

from restdoctor.rest_framework.views import GenericAPIView
from tests.stubs.serializers import BaseObjectSerializer

if typing.TYPE_CHECKING:
    from rest_framework.request import Request
    from restdoctor.rest_framework.custom_types import Parsers


class EmptyView(GenericAPIView):
    serializer_class = BaseObjectSerializer
    parser_classes: Parsers = []

    def get(self, request: Request, *args: typing.Any, **kwargs: typing.Any) -> Response:
        return Response({'data': None})

    def post(self, request: Request, *args: typing.Any, **kwargs: typing.Any) -> Response:
        return Response({'data': None})

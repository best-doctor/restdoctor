from __future__ import annotations
import typing

from rest_framework.response import Response

from restdoctor.rest_framework.resources import ResourceViewSet
from restdoctor.rest_framework.views import GenericAPIView
from restdoctor.rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from tests.stubs.models import MyModel
from tests.stubs.serializers import BaseObjectSerializer, MyModelSerializer, MyModelExtendedSerializer

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


class MyModelViewSet(ModelViewSet):
    serializer_class = MyModelSerializer
    queryset = MyModel.objects.all()


class MyModelExtendedViewSet(ModelViewSet):
    serializer_class = MyModelExtendedSerializer
    queryset = MyModel.objects.all()


class MyModelResourceViewSet(ResourceViewSet):
    resource_views_map = {
        'common': MyModelViewSet,
        'extended': MyModelExtendedViewSet,
    }

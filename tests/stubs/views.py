from __future__ import annotations

import typing

from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from restdoctor.rest_framework.resources import ResourceView, ResourceViewSet
from restdoctor.rest_framework.views import GenericAPIView, ListAPIView
from restdoctor.rest_framework.viewsets import ModelViewSet
from tests.stubs.models import MyModel
from tests.stubs.serializers import (
    BaseObjectSerializer,
    MyModelExtendedSerializer,
    MyModelSerializer,
)

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


class MyModelExtendedAPIView(ListAPIView):
    serializer_class = MyModelSerializer
    queryset = MyModel.objects.all()


class MyModelResourceView(ResourceView):
    resource_views_map = {'extended': MyModelExtendedAPIView}
    resource_actions_map = {'extended': ['list']}
    schema_operation_id_map = {
        'list': 'listMyModelViewResources'  # переопределено, чтобы id не пересекался с MyModelResourceViewSet
    }


class MyModelViewSet(ModelViewSet):
    serializer_class = MyModelSerializer
    queryset = MyModel.objects.all()


class MyModelExtendedViewSet(ModelViewSet):
    serializer_class = MyModelExtendedSerializer
    queryset = MyModel.objects.all()


class MyModelResourceViewSet(ResourceViewSet):
    resource_views_map = {'common': MyModelViewSet, 'extended': MyModelExtendedViewSet}


class MyModelListCreateAPIView(ListCreateAPIView):
    serializer_class = MyModelSerializer
    queryset = MyModel.objects.all()
    action_map = {'get': 'list', 'post': 'create'}


class WithActionsMapResourceView(ResourceView):
    resource_views_map = {'extended': MyModelListCreateAPIView, 'common': MyModelListCreateAPIView}
    resource_actions_map = {'extended': ['list', 'create'], 'common': ['list', 'create']}


class WithoutActionsMapResourceView(ResourceView):
    resource_views_map = {'extended': MyModelListCreateAPIView, 'common': MyModelListCreateAPIView}

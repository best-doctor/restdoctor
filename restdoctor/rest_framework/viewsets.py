from __future__ import annotations

from rest_framework.viewsets import ViewSetMixin as BaseViewSetMixin

from restdoctor.rest_framework.mixins import (
    RetrieveModelMixin,
    ListModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
)
from restdoctor.rest_framework.views import SerializerClassMapApiView


class ViewSetMixin(BaseViewSetMixin):
    pass


class GenericViewSet(ViewSetMixin, SerializerClassMapApiView):
    pass


class ListModelViewSet(
    ListModelMixin,
    GenericViewSet,
):
    pass


class ReadOnlyModelViewSet(
    RetrieveModelMixin,
    ListModelViewSet,
):
    pass


class CreateUpdateReadModelViewSet(
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    ListModelViewSet,
):
    pass


class ModelViewSet(
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    ListModelViewSet,
):
    pass

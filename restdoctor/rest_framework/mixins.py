from __future__ import annotations

import typing

from rest_framework import status
from rest_framework.mixins import (
    ListModelMixin as BaseListModelMixin,
    RetrieveModelMixin as BaseRetrieveModelMixin,
    CreateModelMixin as BaseCreateModelMixin,
    UpdateModelMixin as BaseUpdateModelMixin,
    DestroyModelMixin as BaseDestroyModelMixin,
)
from rest_framework.request import Request
from rest_framework.response import Response

from restdoctor.rest_framework.negotiations import APIVersionContentNegotiation
from restdoctor.rest_framework.pagination import PageNumberPagination

if typing.TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.pagination import BasePagination
    from rest_framework.serializers import BaseSerializer


class NegotiatedMixin:
    content_negotiation_class = APIVersionContentNegotiation


class CreateModelMixin(BaseCreateModelMixin):
    def create(self, request: Request, *args: typing.Any, **kwargs: typing.Any) -> Response:
        request_serializer_class = self.get_request_serializer_class()
        serializer = self.get_serializer_instance(
            request_serializer_class, stage='request', data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        response_serializer_class = self.get_response_serializer_class()
        if response_serializer_class != request_serializer_class:
            serializer = self.get_serializer_instance(
                response_serializer_class, serializer.instance, stage='response')
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ListModelMixin(BaseListModelMixin):
    pagination_class: typing.Optional[BasePagination] = PageNumberPagination

    def get_serializer(self, *args: typing.Any, **kwargs: typing.Any) -> BaseSerializer:
        return self.get_response_serializer(*args, **kwargs)

    def list(self, request: Request, *args: typing.Any, **kwargs: typing.Any) -> Response:  # noqa: A003
        request_serializer = self.get_request_serializer(data=request.query_params, use_default=False)
        request_serializer.is_valid(raise_exception=True)
        queryset = self.get_collection(request_serializer)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_collection(self, request_serializer: BaseSerializer) -> typing.Union[typing.List, QuerySet]:
        return self.filter_queryset(self.get_queryset())


class RetrieveModelMixin(BaseRetrieveModelMixin):
    def get_serializer(self, *args: typing.Any, **kwargs: typing.Any) -> BaseSerializer:
        return self.get_response_serializer(*args, **kwargs)


class UpdateModelMixin(BaseUpdateModelMixin):
    def update(self, request: Request, *args: typing.Any, **kwargs: typing.Any) -> Response:
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        request_serializer_class = self.get_request_serializer_class()
        serializer = self.get_serializer_instance(
            request_serializer_class, instance, stage='request', data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(serializer.instance, '_prefetched_objects_cache', None):
            serializer.instance._prefetched_objects_cache = {}

        response_serializer_class = self.get_response_serializer_class()
        if response_serializer_class != request_serializer_class:
            serializer = self.get_serializer_instance(
                response_serializer_class, serializer.instance, stage='response')
        return Response(serializer.data)


class DestroyModelMixin(BaseDestroyModelMixin):
    pass

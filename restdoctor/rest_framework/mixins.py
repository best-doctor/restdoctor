from __future__ import annotations

import typing

from rest_framework import status
from rest_framework.mixins import CreateModelMixin as BaseCreateModelMixin
from rest_framework.mixins import DestroyModelMixin as BaseDestroyModelMixin
from rest_framework.mixins import ListModelMixin as BaseListModelMixin
from rest_framework.mixins import RetrieveModelMixin as BaseRetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin as BaseUpdateModelMixin
from rest_framework.request import Request
from rest_framework.response import Response

from restdoctor.rest_framework.negotiations import APIVersionContentNegotiation
from restdoctor.rest_framework.pagination import PageNumberPagination
from restdoctor.rest_framework.response import ResponseWithMeta
from restdoctor.rest_framework.serializers import EmptySerializer

if typing.TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.pagination import BasePagination
    from rest_framework.serializers import BaseSerializer

    from restdoctor.rest_framework.custom_types import ModelObject


class NegotiatedMixin:
    content_negotiation_class = APIVersionContentNegotiation


class CreateModelMixin(BaseCreateModelMixin):
    def create(self, request: Request, *args: typing.Any, **kwargs: typing.Any) -> Response:
        request_serializer_class = self.get_request_serializer_class()
        serializer = self.get_serializer_instance(
            request_serializer_class, stage='request', data=request.data
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        response_serializer_class = self.get_response_serializer_class()
        if response_serializer_class != request_serializer_class:
            serializer = self.get_serializer_instance(
                response_serializer_class, serializer.instance, stage='response'
            )
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ListModelMixin(BaseListModelMixin):
    pagination_class: typing.Optional[BasePagination] = PageNumberPagination

    def get_serializer(self, *args: typing.Any, **kwargs: typing.Any) -> BaseSerializer:
        return self.get_response_serializer(*args, **kwargs)

    def list(  # noqa: A003
        self, request: Request, *args: typing.Any, **kwargs: typing.Any
    ) -> Response:
        request_serializer = self.get_request_serializer(
            data=request.query_params, use_default=False
        )
        request_serializer.is_valid(raise_exception=True)
        queryset = self.get_collection(request_serializer)
        meta = self.get_meta_serializer_data()
        page = self.paginate_queryset(queryset)
        if page is not None:
            self.perform_list(page)
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.meta.update(meta)
            return response

        self.perform_list(queryset)

        serializer = self.get_serializer(queryset, many=True)
        return ResponseWithMeta(data=serializer.data, meta=meta)

    def get_collection(
        self, request_serializer: BaseSerializer
    ) -> typing.Union[typing.List, QuerySet]:
        return self.filter_queryset(self.get_queryset())

    def perform_list(self, data: typing.Union[typing.List, QuerySet]) -> None:
        pass

    def get_meta_data(self) -> typing.Dict[str, typing.Any]:
        return {}

    def get_meta_serializer_data(self) -> typing.Dict[str, typing.Any]:
        if issubclass(self.get_meta_serializer_class(), EmptySerializer):
            return {}
        serializer = self.get_meta_serializer(self.get_meta_data())
        return serializer.data


class RetrieveModelMixin(BaseRetrieveModelMixin):
    def retrieve(self, request: Request, *args: typing.Any, **kwargs: typing.Any) -> Response:
        request_serializer = self.get_request_serializer(
            data=request.query_params, use_default=False
        )
        request_serializer.is_valid(raise_exception=True)

        item = self.get_item(request_serializer)

        serializer = self.get_serializer(item)
        return Response(serializer.data)

    def get_item(
        self, request_serializer: BaseSerializer
    ) -> typing.Union[typing.Dict, ModelObject]:
        return self.get_object()

    def get_serializer(self, *args: typing.Any, **kwargs: typing.Any) -> BaseSerializer:
        return self.get_response_serializer(*args, **kwargs)


class UpdateModelMixin(BaseUpdateModelMixin):
    def update(self, request: Request, *args: typing.Any, **kwargs: typing.Any) -> Response:
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        request_serializer_class = self.get_request_serializer_class()
        serializer = self.get_serializer_instance(
            request_serializer_class, instance, stage='request', data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(serializer.instance, '_prefetched_objects_cache', None):
            serializer.instance._prefetched_objects_cache = {}

        response_serializer_class = self.get_response_serializer_class()
        if response_serializer_class != request_serializer_class:
            serializer = self.get_serializer_instance(
                response_serializer_class, serializer.instance, stage='response'
            )
        return Response(serializer.data)


class DestroyModelMixin(BaseDestroyModelMixin):
    pass

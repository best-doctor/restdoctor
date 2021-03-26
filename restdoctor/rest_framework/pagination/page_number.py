from __future__ import annotations

import typing

from django.utils.translation import gettext_lazy as _
from rest_framework.pagination import BasePagination
from rest_framework.utils.urls import replace_query_param
from rest_framework.exceptions import NotFound

from restdoctor.constants import DEFAULT_MAX_PAGE_SIZE, DEFAULT_PAGE_SIZE
from restdoctor.rest_framework.pagination.mixins import SerializerClassPaginationMixin
from restdoctor.rest_framework.pagination.serializers import (
    PageNumberRequestSerializer, PageNumberResponseSerializer, PageNumberUncountedResponseSerializer,
)
from restdoctor.rest_framework.response import ResponseWithMeta

if typing.TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.request import Request
    from rest_framework.views import APIView

    from restdoctor.rest_framework.pagination.custom_types import OptionalList


class PageNumberPagination(SerializerClassPaginationMixin, BasePagination):
    use_count = True
    page_query_param = 'page'
    page_size_query_param = 'per_page'
    serializer_class_map = {
        'default': PageNumberRequestSerializer,
        'pagination': {
            'response': PageNumberResponseSerializer,
        },
    }

    max_page_size = DEFAULT_MAX_PAGE_SIZE
    default_page_size = DEFAULT_PAGE_SIZE

    invalid_page_message = _('Invalid page.')

    def paginate_queryset(
        self, queryset: QuerySet, request: Request, view: APIView = None,
    ) -> OptionalList:
        serializer_class = self.get_request_serializer_class()
        serializer = serializer_class(data=request.query_params, max_per_page=self.max_page_size)
        serializer.is_valid(raise_exception=False)

        self.per_page = serializer.validated_data.get(self.page_size_query_param, self.default_page_size)
        self.page = serializer.validated_data.get(self.page_query_param, 1)

        self.has_next = False
        self.has_prev = (self.page > 1)

        base_url = request.build_absolute_uri()
        self.base_url = replace_query_param(base_url, self.page_size_query_param, self.per_page)
        self.request = request

        start_offset = (self.page - 1) * self.per_page
        stop_offset = start_offset + self.per_page + 1

        if self.use_count:
            self.total = len(queryset) if isinstance(queryset, list) else queryset.count()
            if self.total and self.per_page:
                self.pages, rem = divmod(self.total, self.per_page)
                if rem:
                    self.pages += 1
            else:
                self.pages = 1
            if self.page > self.pages:
                msg = self.invalid_page_message.format(page_number=self.page)
                raise NotFound(msg)

        paginated = list(queryset[start_offset:stop_offset])

        if len(paginated) > self.per_page:
            self.has_next = True
            del paginated[-1]

        return paginated

    def get_page_link_tmpl(self) -> str:
        url_tmpl = self.request.build_absolute_uri()
        url_tmpl = replace_query_param(url_tmpl, self.page_size_query_param, self.per_page)
        return url_tmpl

    def get_page_link(self, page: typing.Any = 1) -> typing.Optional[str]:
        if page:
            return replace_query_param(self.base_url, self.page_query_param, page)

    def get_paginated_response(self, data: typing.Sequence[typing.Any]) -> ResponseWithMeta:
        meta = {
            self.page_query_param: self.page,
            self.page_size_query_param: self.per_page,
            'url': self.get_page_link(page=self.page),
        }
        if self.use_count:
            meta['total'] = self.total

        if self.use_count and self.pages > 1:
            meta['last_url'] = self.get_page_link(page=self.pages)
        meta['next_url'] = self.get_page_link(page=self.page + 1) if self.has_next else None
        meta['prev_url'] = self.get_page_link(page=self.page - 1) if self.has_prev else None

        return ResponseWithMeta(data=data, meta=meta)


class PageNumberUncountedPagination(PageNumberPagination):
    use_count = False

    serializer_class_map = {
        'default': PageNumberRequestSerializer,
        'pagination': {
            'response': PageNumberUncountedResponseSerializer,
        },
    }

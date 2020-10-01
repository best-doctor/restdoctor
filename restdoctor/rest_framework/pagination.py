from __future__ import annotations

import contextlib
import typing
import uuid

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from rest_framework.fields import IntegerField, UUIDField
from rest_framework.pagination import BasePagination
from rest_framework.serializers import Serializer
from rest_framework.utils.urls import replace_query_param, remove_query_param
from rest_framework.exceptions import NotFound

from restdoctor.constants import DEFAULT_PAGE_SIZE, DEFAULT_MAX_PAGE_SIZE
from restdoctor.rest_framework.response import ResponseWithMeta

if typing.TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.request import Request
    from rest_framework.views import APIView

    from restdoctor.rest_framework.custom_types import OpenAPISchema

    OptionalList = typing.Optional[typing.List[typing.Any]]
    Lookup = typing.Dict[str, typing.Any]
    OptionalLookup = typing.Optional[Lookup]


class PerPageSerializerBase(Serializer):
    per_page = IntegerField(default=DEFAULT_PAGE_SIZE, allow_null=True,
                            help_text='Количество элементов на странице')

    def __init__(
        self, max_per_page: int = 200,
        *args: typing.Any, **kwargs: typing.Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.max_per_page = max_per_page

    def validate_per_page(self, value: typing.Optional[int]) -> typing.Optional[int]:
        if value and value > self.max_per_page:
            return self.max_per_page
        return value


class PaginatorSerializer(PerPageSerializerBase):
    page = IntegerField(min_value=1, default=1, help_text='Выбранная страница, начиная с 1')


class PageNumberPagination(BasePagination):
    use_count = True
    page_query_param = 'page'
    page_size_query_param = 'per_page'
    serializer_class = PaginatorSerializer

    max_page_size = DEFAULT_MAX_PAGE_SIZE

    invalid_page_message = _('Invalid page.')

    def paginate_queryset(
        self, queryset: QuerySet, request: Request, view: APIView = None,
    ) -> OptionalList:
        serializer = self.serializer_class(data=request.query_params, max_per_page=self.max_page_size)
        serializer.is_valid(raise_exception=False)

        self.per_page = serializer.validated_data.get('per_page')
        self.page = serializer.validated_data.get('page', 1)

        if not self.per_page:
            return None

        self.has_next = False
        self.has_prev = (self.page > 1)

        base_url = request.build_absolute_uri()
        self.base_url = replace_query_param(base_url, self.page_size_query_param, self.per_page)
        self.request = request

        start_offset = (self.page - 1) * self.per_page
        stop_offset = start_offset + self.per_page + 1

        if self.use_count:
            self.total = len(queryset) if isinstance(queryset, list) else queryset.count()
            if self.total:
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

    def get_paginated_response_schema(self, schema: OpenAPISchema) -> OpenAPISchema:
        meta = schema['properties'].get('meta', {'type': 'object', 'properties': {}})
        meta['properties'] = {
            self.page_query_param: {
                'type': 'integer',
            },
            self.page_size_query_param: {
                'type': 'integer',
                'example': 20,
                'maximum': self.max_page_size,
            },
            'total': {
                'type': 'integer',
                'example': 100500,
            },
            'last_url': {
                'type': 'string',
                'nullable': True,
            },
            'next_url': {
                'type': 'string',
                'nullable': True,
            },
            'prev_url': {
                'type': 'string',
                'nullable': True,
            },
        }
        schema['properties']['meta'] = meta
        return schema


class PageNumberUncountedPagination(PageNumberPagination):
    use_count = False


class CursorUUIDSerializer(PerPageSerializerBase):
    after = UUIDField(required=False, allow_null=True)
    before = UUIDField(required=False, allow_null=True)


def get_order(default_order: str, serializer_keys: typing.Sequence[str]) -> str:
    if 'after' in serializer_keys:
        return 'after'
    if 'before' in serializer_keys:
        return 'before'
    return default_order


def get_cursor(
    queryset: QuerySet,
    after_uuid: uuid.UUID = None,
    before_uuid: uuid.UUID = None,
    default_order: str = None,
) -> typing.Tuple[typing.Any, str]:
    cursor_obj = None
    if after_uuid is not None:
        with contextlib.suppress(ObjectDoesNotExist):
            cursor_obj = queryset.get(uuid=after_uuid)
            order = 'after'
    elif before_uuid is not None:
        with contextlib.suppress(ObjectDoesNotExist):
            cursor_obj = queryset.get(uuid=before_uuid)
            order = 'before'
    if cursor_obj is None:
        order = default_order or ''
    return cursor_obj, order


class CursorUUIDPagination(BasePagination):
    use_count = True

    after_query_param = 'after'
    before_query_param = 'before'
    page_size_query_param = 'per_page'

    lookup_by_field = 'timestamp'
    order_by_field = 'timestamp'
    default_order = 'before'

    serializer_class = CursorUUIDSerializer

    max_page_size = DEFAULT_MAX_PAGE_SIZE

    def get_lookup(self) -> OptionalLookup:
        if self.cursor_obj:
            lookup_operator = 'gt' if self.order == 'after' else 'lt'
            lookup_keyword = f'{self.lookup_by_field}__{lookup_operator}'
            return {lookup_keyword: getattr(self.cursor_obj, self.lookup_by_field)}

    def paginate_queryset(
        self, queryset: QuerySet, request: Request, view: APIView = None,
    ) -> OptionalList:
        serializer = self.serializer_class(data=request.query_params, max_per_page=self.max_page_size)
        serializer.is_valid(raise_exception=True)

        self.per_page = serializer.validated_data.get(self.page_size_query_param)

        if not self.per_page:
            return None

        after_uuid = serializer.validated_data.get(self.after_query_param)
        before_uuid = serializer.validated_data.get(self.before_query_param)

        order = get_order(self.default_order, serializer.validated_data.keys())
        self.cursor_obj, self.order = get_cursor(queryset, after_uuid, before_uuid, order)

        lookup = self.get_lookup()
        if lookup:
            queryset = queryset.filter(**lookup)

        order_sign = '-' if self.order == 'before' else ''
        order_keyword = f'{order_sign}{self.order_by_field}'
        queryset = queryset.order_by(order_keyword)

        base_url = request.build_absolute_uri()
        self.base_url = replace_query_param(base_url, self.page_size_query_param, self.per_page)
        self.request = request
        self.has_next = False

        start_offset = 0
        stop_offset = start_offset + self.per_page + 1

        if self.use_count:
            self.total = queryset.count()

        paginated = list(queryset[:stop_offset])

        if len(paginated) > self.per_page:
            self.has_next = True
            del paginated[-1]

        if paginated:
            self.page_boundaries = (
                paginated[0].uuid,
                paginated[-1].uuid,
            )
        elif self.cursor_obj:
            self.page_boundaries = (self.cursor_obj.uuid, self.cursor_obj.uuid)
        else:
            self.page_boundaries = (None, None)

        return paginated

    def get_page_link_tmpl(self) -> str:
        url_tmpl = self.request.build_absolute_uri()
        url_tmpl = replace_query_param(url_tmpl, self.page_size_query_param, self.per_page)
        return url_tmpl

    def get_page_link(self, after: typing.Any = None, before: typing.Any = None) -> typing.Optional[str]:
        if after is not None:
            base_url = remove_query_param(self.base_url, self.before_query_param)
            return replace_query_param(base_url, self.after_query_param, after)
        if before is not None:
            base_url = remove_query_param(self.base_url, self.after_query_param)
            return replace_query_param(base_url, self.before_query_param, before)

    def get_paginated_response(self, data: typing.Sequence[typing.Any]) -> ResponseWithMeta:
        meta = {
            self.page_size_query_param: self.per_page,
            'has_next': self.has_next,
        }
        cursor_uuid = None
        if self.cursor_obj:
            cursor_uuid = self.cursor_obj.uuid
        meta[self.order] = cursor_uuid
        meta['url'] = self.get_page_link(**{self.order: cursor_uuid or ''})

        if self.use_count:
            meta['total'] = self.total

        if self.page_boundaries[0]:
            after_idx, before_idx = 0, 1
            if self.order == 'after':
                after_idx, before_idx = 1, 0

            meta['after_url'] = self.get_page_link(
                **{self.after_query_param: self.page_boundaries[after_idx]})
            meta['before_url'] = self.get_page_link(
                **{self.before_query_param: self.page_boundaries[before_idx]})

        return ResponseWithMeta(data=data, meta=meta)

    def get_paginated_response_schema(self, schema: OpenAPISchema) -> OpenAPISchema:
        meta = schema['properties'].get('meta', {'type': 'object', 'properties': {}})
        meta['properties'] = {
            self.page_size_query_param: {
                'type': 'integer',
                'maximum': self.max_page_size,
                'example': 20,
            },
            'has_next': {
                'type': 'boolean',
                'example': True,
            },
            'before': {
                'type': 'uuid',
                'nullable': True,
                'required': False,
            },
            'after': {
                'type': 'uuid',
                'nullable': True,
                'required': False,
            },
            'total': {
                'type': 'integer',
                'example': 123,
                'required': False,
            },
            'url': {
                'type': 'string',
                'nullable': False,
            },
            'last_url': {
                'type': 'string',
                'nullable': True,
            },
            'after_url': {
                'type': 'string',
                'nullable': True,
            },
            'before_url': {
                'type': 'string',
                'nullable': True,
            },
        }
        schema['properties']['meta'] = meta
        return schema


class CursorUUIDUncountedPagination(PageNumberPagination):
    use_count = False

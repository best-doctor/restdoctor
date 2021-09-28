from __future__ import annotations

import typing

from restdoctor.utils.serializers import get_serializer_class_from_map

if typing.TYPE_CHECKING:
    from restdoctor.rest_framework.schema.custom_types import OpenAPISchema, ViewSchemaBase
    from restdoctor.utils.serializers import SerializerClassMap, SerializerType


class SerializerClassPaginationMixin:
    view_schema: typing.Optional[ViewSchemaBase]
    serializer_class: SerializerType
    serializer_class_map: SerializerClassMap

    def __init__(self, *args: typing.Any, view_schema: ViewSchemaBase = None, **kwargs: typing.Any):
        self.view_schema = view_schema
        super().__init__(*args, **kwargs)  # type: ignore

    def get_request_serializer_class(self) -> SerializerType:
        return get_serializer_class_from_map('pagination', 'request', self.serializer_class_map)

    def get_response_serializer_class(self) -> SerializerType:
        return get_serializer_class_from_map('pagination', 'response', self.serializer_class_map)

    def get_paginated_response_schema(self, schema: OpenAPISchema) -> OpenAPISchema:
        if self.view_schema:
            serializer_class = self.get_response_serializer_class()
            response_serializer = serializer_class()
            schema['properties']['meta'] = self.view_schema.get_serializer_schema(
                response_serializer
            )
        return schema

from __future__ import annotations

import typing as t

from rest_framework.fields import Field
from rest_framework.schemas.openapi import SchemaGenerator
from rest_framework.serializers import BaseSerializer

OpenAPISchema = t.Dict[str, 'OpenAPISchema']  # type: ignore
LocalRefs = t.Dict[t.Tuple[str, ...], t.Any]

ResponseCode = str
ActionDescription = str

CodeActionSchemaTuple = t.Tuple[ResponseCode, ActionDescription, t.Optional[OpenAPISchema]]  # type: ignore
CodeDescriptionTuple = t.Tuple[ResponseCode, ActionDescription]


class ViewSchemaProtocol(t.Protocol):
    generator: t.Optional[SchemaGenerator] = None
    serializer_schema: SerializerSchemaProtocol
    field_schema: FieldSchemaProtocol

    def get_field_schema(self, field: Field) -> OpenAPISchema:
        return self.field_schema.get_field_schema(field)

    def get_serializer_schema(
        self,
        serializer: BaseSerializer,
        write_only: bool = True,
        read_only: bool = True,
        required: bool = True,
    ) -> OpenAPISchema:
        return self.serializer_schema.get_serializer_schema(
            serializer, write_only=write_only, read_only=read_only, required=required
        )

    def map_field(self, field: Field) -> t.Optional[OpenAPISchema]:
        return self.field_schema.map_field(field)

    def get_field_description(self, field: Field) -> t.Optional[str]:
        return self.field_schema.get_field_description(field)

    def map_field_validators(self, field: Field, schema: OpenAPISchema) -> None:
        return self.field_schema.map_field_validators(field, schema)

    def map_serializer(
        self,
        serializer: BaseSerializer,
        write_only: bool = True,
        read_only: bool = True,
        required: bool = True,
    ) -> OpenAPISchema:
        return self.serializer_schema.map_serializer(
            serializer, write_only=write_only, read_only=read_only, required=required
        )

    def map_query_serializer(self, serializer: BaseSerializer) -> t.List[OpenAPISchema]:
        return self.serializer_schema.map_query_serializer(serializer)


class SerializerSchemaProtocol(t.Protocol):
    view_schema: ViewSchemaProtocol

    def get_serializer_schema(
        self,
        serializer: BaseSerializer,
        write_only: bool = True,
        read_only: bool = True,
        required: bool = True,
    ) -> OpenAPISchema:
        ...

    def map_serializer(
        self,
        serializer: BaseSerializer,
        write_only: bool = True,
        read_only: bool = True,
        required: bool = True,
    ) -> OpenAPISchema:
        ...

    def map_query_serializer(self, serializer: BaseSerializer) -> t.List[OpenAPISchema]:
        ...


class FieldSchemaProtocol(t.Protocol):
    view_schema: ViewSchemaProtocol

    def get_field_schema(self, field: Field) -> OpenAPISchema:
        ...

    def map_field(self, field: Field) -> t.Optional[OpenAPISchema]:
        ...

    def get_field_description(self, field: Field) -> t.Optional[str]:
        ...

    def map_field_validators(self, field: Field, schema: OpenAPISchema) -> None:
        ...

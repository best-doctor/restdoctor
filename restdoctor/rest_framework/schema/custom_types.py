from __future__ import annotations
import typing as t
from rest_framework.fields import Field
from rest_framework.serializers import BaseSerializer


OpenAPISchema = t.Dict[str, 'OpenAPISchema']  # type: ignore
LocalRefs = t.Dict[t.Tuple[str, ...], t.Any]

ResponseCode = str
ActionDescription = str

CodeActionSchemaTuple = t.Tuple[ResponseCode, ActionDescription, t.Optional[OpenAPISchema]]  # type: ignore
CodeDescriptionTuple = t.Tuple[ResponseCode, ActionDescription]


class ViewSchemaProtocol(t.Protocol):
    serializer_schema: SerializerSchemaProtocol

    def get_field_schema(self, field: Field) -> OpenAPISchema:
        return self.serializer_schema.get_field_schema(field)

    def get_serializer_schema(
        self, serializer: BaseSerializer,
        write_only: bool = True, read_only: bool = True, required: bool = True,
    ) -> OpenAPISchema:
        return self.serializer_schema.get_serializer_schema(
            serializer, write_only=write_only, read_only=read_only, required=required,
        )

    def map_field(self, field: Field) -> OpenAPISchema:
        ...


class SerializerSchemaProtocol(t.Protocol):
    view_schema: ViewSchemaProtocol

    def __init__(self, view_schema: ViewSchemaProtocol):
        self.view_schema = view_schema

    def get_field_schema(self, field: Field) -> OpenAPISchema:
        ...

    def get_field_description(self, field: Field) -> t.Optional[str]:
        ...

    def map_field_validators(self, field: Field, schema: OpenAPISchema) -> None:
        ...

    def get_serializer_schema(
        self, serializer: BaseSerializer,
        write_only: bool = True, read_only: bool = True, required: bool = True,
    ) -> OpenAPISchema:
        ...

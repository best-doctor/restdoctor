from __future__ import annotations

import copy
import typing

from django.utils.encoding import force_str
from pydantic.schema import schema as pydantic_schema
from rest_framework.fields import HiddenField
from rest_framework.serializers import BaseSerializer

from restdoctor.rest_framework.schema.custom_types import (
    OpenAPISchema,
    SerializerSchemaBase,
    ViewSchemaBase,
)
from restdoctor.rest_framework.serializers import PydanticSerializer

OPENAPI_REF_PREFIX = '#/components/schemas/'


def fix_pydantic_title(schema: OpenAPISchema) -> OpenAPISchema:
    fixed_schema = copy.deepcopy(schema)
    if 'title' in fixed_schema:
        if 'description' not in fixed_schema:
            fixed_schema['description'] = fixed_schema.get('title', '')
        del fixed_schema['title']

    for item_name, item_schema in fixed_schema.items():
        if isinstance(item_schema, dict):
            fixed_schema[item_name] = fix_pydantic_title(item_schema)
    return fixed_schema


class SerializerSchema(SerializerSchemaBase):
    def __init__(self, view_schema: ViewSchemaBase):
        self.view_schema = view_schema

    def map_serializer_fields(
        self,
        serializer: BaseSerializer,
        include_write_only: bool = True,
        include_read_only: bool = True,
    ) -> typing.Tuple[OpenAPISchema, typing.List[str]]:
        required_list = []
        properties = {}

        for field in serializer.fields.values():
            if (
                isinstance(field, HiddenField)
                or (field.write_only and not include_write_only)
                or (field.read_only and not include_read_only)
            ):
                continue
            if field.required:
                required_list.append(field.field_name)
            field_schema = self.view_schema.get_field_schema(field)
            if field_schema:
                properties[field.field_name] = field_schema
        return properties, required_list

    def get_serializer_schema(
        self,
        serializer: BaseSerializer,
        write_only: bool = True,
        read_only: bool = True,
        required: bool = True,
    ) -> OpenAPISchema:
        if isinstance(serializer, PydanticSerializer):
            return fix_pydantic_title(serializer.pydantic_model.schema())

        properties, required_list = self.map_serializer_fields(
            serializer, include_write_only=write_only, include_read_only=read_only
        )

        if not properties:
            return {}

        schema: OpenAPISchema = {'type': 'object', 'properties': properties}
        if serializer.__doc__:
            schema['description'] = serializer.__doc__
        if required and required_list:
            schema['required'] = required_list
        return schema

    def get_ref_name(
        self,
        serializer: BaseSerializer,
        write_only: bool = True,
        read_only: bool = True,
        required: bool = True,
    ) -> str:
        serializer_module_name = serializer.__module__.split('.')[0]
        serializer_class_name = serializer.__class__.__name__

        suffixes = []
        if write_only:
            suffixes.append('W')
        if read_only:
            suffixes.append('R')
        if required:
            suffixes.append('Q')

        suffix = ''.join(suffixes)

        if serializer_class_name.endswith('Serializer'):
            serializer_class_name = serializer_class_name[:-10]
        return f'{OPENAPI_REF_PREFIX}{serializer_module_name}_{serializer_class_name}{suffix}'

    def get_pydantic_ref_name(self, serializer_class_name: str) -> str:
        if serializer_class_name.endswith('Serializer'):
            serializer_class_name = serializer_class_name[:-10]

        return f'{OPENAPI_REF_PREFIX}{serializer_class_name}'

    def map_pydantic_serializer(self, serializer: PydanticSerializer) -> OpenAPISchema:
        if not self.view_schema.generator:
            return fix_pydantic_title(serializer.pydantic_model.schema())

        schema = {}
        ref_repo = pydantic_schema([serializer.pydantic_model], ref_prefix=OPENAPI_REF_PREFIX)
        for class_name, definition in ref_repo['definitions'].items():
            definition = fix_pydantic_title(definition)
            ref = self.get_pydantic_ref_name(class_name)
            self.view_schema.generator.local_refs_registry.put_local_ref(ref, definition)
            if class_name == serializer.pydantic_model.__name__:
                schema = {'$ref': ref}

        return schema

    def map_serializer(
        self,
        serializer: BaseSerializer,
        write_only: bool = True,
        read_only: bool = True,
        required: bool = True,
    ) -> OpenAPISchema:
        if isinstance(serializer, PydanticSerializer):
            return self.map_pydantic_serializer(serializer)

        schema = self.get_serializer_schema(
            serializer, write_only=write_only, read_only=read_only, required=required
        )

        if schema and self.view_schema.generator:
            ref = self.get_ref_name(
                serializer, write_only=write_only, read_only=read_only, required=required
            )
            self.view_schema.generator.local_refs_registry.put_local_ref(ref, schema)
            schema = {'$ref': ref}

        return schema

    def map_query_serializer(self, serializer: BaseSerializer) -> typing.List[OpenAPISchema]:
        props = []

        for field in serializer.fields.values():
            if isinstance(field, HiddenField):
                continue

            prop = {
                'name': field.field_name,
                'in': 'query',
                'required': field.required,
                'schema': self.view_schema.get_field_schema(field),
            }

            if field.help_text:
                prop['description'] = force_str(field.help_text)

            props.append(prop)

        return props

from __future__ import annotations
import typing

from django.conf import settings
from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured
from django.core.validators import RegexValidator
from rest_framework.fields import HiddenField, Field, ModelField, empty
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.serializers import BaseSerializer, ModelSerializer

from restdoctor.rest_framework.schema.custom_types import (
    SerializerSchemaProtocol, OpenAPISchema, ViewSchemaProtocol,
)


class SerializerSchema(SerializerSchemaProtocol):
    def __init__(self, view_schema: ViewSchemaProtocol):
        self.view_schema = view_schema

    def get_field_schema(self, field: Field) -> OpenAPISchema:
        schema = self.view_schema.map_field(field)
        if field.read_only:
            schema['readOnly'] = True
        if field.write_only:
            schema['writeOnly'] = True
        if field.allow_null:
            schema['nullable'] = True
        if field.default and field.default != empty and not callable(field.default):
            schema['default'] = field.default
        description = self.get_field_description(field)
        if description:
            schema['description'] = description

        self.map_field_validators(field, schema)

        return schema

    def get_field_description(self, field: Field) -> typing.Optional[str]:
        field_description = None
        if field.help_text:
            field_description = str(field.help_text)
        elif isinstance(field.parent, ModelSerializer):
            if isinstance(field, ModelField):
                field_description = field.model_field.verbose_name
            elif field.source != '*':
                try:
                    field_description = str(
                        field.parent.Meta.model._meta.get_field(field.source).verbose_name)
                except (AttributeError, LookupError, FieldDoesNotExist):
                    pass

        if settings.API_STRICT_SCHEMA_VALIDATION and not field_description:
            raise ImproperlyConfigured(
                f'field {field.field_name} in serializer {field.parent.__class__.__name__} '
                f'should have help_text argument or verbose_name in source model field',
            )

        return field_description

    def map_field_validators(self, field: Field, schema: OpenAPISchema) -> None:
        AutoSchema.map_field_validators(self, field, schema)

        # Backported from django-rest-framework
        # https://github.com/encode/django-rest-framework/commit/5ce237e00471d885f05e6d979ec777552809b3b1
        for validator in field.validators:
            if isinstance(validator, RegexValidator):
                schema['pattern'] = validator.regex.pattern.replace('\\Z', '\\z')

    def get_serializer_schema(
        self, serializer: BaseSerializer,
        write_only: bool = True, read_only: bool = True, required: bool = True,
    ) -> OpenAPISchema:
        required_list = []
        properties = {}

        for field in serializer.fields.values():
            if (
                isinstance(field, HiddenField)
                or (field.write_only and not write_only)
                or (field.read_only and not read_only)
            ):
                continue
            if field.required:
                required_list.append(field.field_name)

            properties[field.field_name] = self.get_field_schema(field)

        if not properties:
            return {}

        schema: OpenAPISchema = {
            'type': 'object',
            'properties': properties,
        }
        if serializer.__doc__:
            schema['description'] = serializer.__doc__
        if required and required_list:
            schema['required'] = required_list
        return schema

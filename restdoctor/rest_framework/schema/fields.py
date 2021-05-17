from __future__ import annotations

import collections
import contextlib
import decimal
import typing

from django.conf import settings
from django.contrib.gis.db.models import PointField
from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured
from django.core.validators import RegexValidator
from django.db.models import AutoField
from rest_framework.fields import (
    BooleanField,
    ChoiceField,
    DateField,
    DateTimeField,
    DecimalField,
    DictField,
    EmailField,
    Field,
    FileField,
    FloatField,
    HStoreField,
    IntegerField,
    IPAddressField,
    JSONField,
    ListField,
    ModelField,
    MultipleChoiceField,
    SerializerMethodField,
    URLField,
    UUIDField,
    _UnvalidatedField,
    empty,
)
from rest_framework.relations import ManyRelatedField, PrimaryKeyRelatedField
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.serializers import BaseSerializer, ListSerializer, ModelSerializer, Serializer
from rest_framework.settings import api_settings

from restdoctor.rest_framework.schema.custom_types import (
    FieldSchemaProtocol,
    OpenAPISchema,
    ViewSchemaProtocol,
)
from restdoctor.utils.typing_inspect import is_list_type, is_optional_type


def array_schema(item_schema: OpenAPISchema = None) -> OpenAPISchema:
    schema: OpenAPISchema = {'type': 'array'}
    if item_schema:
        schema['items'] = item_schema
    return schema


def string_schema(string_format: str = None) -> OpenAPISchema:
    schema: OpenAPISchema = {'type': 'string'}
    if string_format:
        schema['format'] = string_format
    return schema


def drf_map_field_validators(obj: FieldSchemaProtocol, field: Field, schema: OpenAPISchema) -> None:
    try:
        AutoSchema.map_field_validators(obj, field, schema)
    except AttributeError:
        AutoSchema._map_field_validators(obj, field, schema)


class FieldSchema(FieldSchemaProtocol):
    def __init__(self, view_schema: ViewSchemaProtocol):
        self.view_schema = view_schema

    @classmethod
    def check_method_field_annotations(cls, field: Field, field_wrapper: Field) -> None:
        field_name = field_wrapper.field_name
        try:
            return_annotation = typing.get_type_hints(
                getattr(field_wrapper.parent, f'get_{field_name}')
            )['return']
        except NameError:
            # We don't see types included with TYPE_CHECKING == True
            return
        field_allow_null = getattr(field, 'allow_null', True)
        if field_allow_null ^ is_optional_type(return_annotation):
            serializer_name = field_wrapper.parent.__class__.__name__
            raise ImproperlyConfigured(
                f'Field {field_name} in {serializer_name} '
                f"doesn't match with it's annotation: allow_null={field_allow_null} "
                f'vs {return_annotation}'
            )

        field_many = getattr(field, 'many', False) or isinstance(
            field, (ListField, MultipleChoiceField)
        )
        if field_many ^ is_list_type(return_annotation):
            serializer_name = field_wrapper.parent.__class__.__name__
            raise ImproperlyConfigured(
                f'Field {field_name} in {serializer_name} '
                f"doesn't match with it's annotation: many={field_many} "
                f'vs {return_annotation}'
            )

    def get_field_schema(self, field: Field) -> OpenAPISchema:
        schema = self.map_field(field)
        if not schema:
            return {}
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
                with contextlib.suppress(AttributeError, LookupError, FieldDoesNotExist):
                    field_description = str(
                        field.parent.Meta.model._meta.get_field(field.source).verbose_name
                    )

        if settings.API_STRICT_SCHEMA_VALIDATION and not field_description:
            raise ImproperlyConfigured(
                f'field {field.field_name} in serializer {field.parent.__class__.__name__} '
                f'should have help_text argument or verbose_name in source model field'
            )

        return field_description

    def map_field_validators(self, field: Field, schema: OpenAPISchema) -> None:
        drf_map_field_validators(self, field, schema)

        # Backported from django-rest-framework
        # https://github.com/encode/django-rest-framework/commit/5ce237e00471d885f05e6d979ec777552809b3b1
        for validator in field.validators:
            if isinstance(validator, RegexValidator):
                schema['pattern'] = validator.regex.pattern.replace('\\Z', '\\z')

    def map_field(self, original_field: Field) -> typing.Optional[OpenAPISchema]:
        # Field.__deepcopy__ сбрасывает кастомные атрибуты, поэтому схему ищем через класс сериализатора
        field = original_field
        if isinstance(field, SerializerMethodField):
            parent_field = field.parent.__class__._declared_fields[field.field_name]
            field = getattr(parent_field, 'schema_type', field)

            if settings.API_STRICT_SCHEMA_VALIDATION:
                self.check_method_field_annotations(field, original_field)

        field_handlers = [
            (_UnvalidatedField, lambda _: None),
            (PointField, self.map_point_field),
            ((ListSerializer, Serializer), self.map_serializer),
            ((ManyRelatedField, PrimaryKeyRelatedField), self.map_related),
            (MultipleChoiceField, self.map_choice_field),
            (ChoiceField, self.map_choice_field),
            (ListField, lambda f: array_schema(self.map_field(f.child))),
            (DateField, lambda _: string_schema('date')),
            (DateTimeField, lambda _: string_schema('date-time')),
            (EmailField, lambda _: string_schema('email')),
            (URLField, lambda _: string_schema('uri')),
            (UUIDField, lambda _: string_schema('uuid')),
            (IPAddressField, self.map_ipaddress_field),
            (DecimalField, self.map_decimal_field),
            ((FloatField, IntegerField), self.map_numeric_field),
            (FileField, lambda _: string_schema('binary')),
            (BooleanField, lambda _: {'type': 'boolean'}),
            ((JSONField, DictField, HStoreField), lambda _: {'type': 'object'}),
            (Field, lambda _: string_schema()),
            # Catch-all type
            (object, lambda _: string_schema()),
        ]

        for field_types, handler in field_handlers:
            if isinstance(field, field_types):
                return handler(field)

    def map_choice_field(self, field: ChoiceField) -> OpenAPISchema:
        choices = list(
            collections.OrderedDict.fromkeys(field.choices)
        )  # preserve order and remove duplicates
        schema: OpenAPISchema = {'enum': choices}

        choice_type = None
        if all(isinstance(choice, bool) for choice in choices):
            choice_type = 'boolean'
        elif all(isinstance(choice, int) for choice in choices):
            choice_type = 'integer'
        elif all(isinstance(choice, (int, float, decimal.Decimal)) for choice in choices):
            choice_type = 'number'
        elif all(isinstance(choice, str) for choice in choices):
            choice_type = 'string'

        if choice_type:
            schema['type'] = choice_type

        if isinstance(field, MultipleChoiceField):
            return array_schema(schema)
        return schema

    def map_point_field(self, field: PointField) -> OpenAPISchema:
        return {
            'type': {'type': 'Point'},
            'coordinates': {
                'type': 'array',
                'items': {'type': 'number', 'format': 'float'},
                'example': [12.9721, 77.5933],
                'minItems': 2,
                'maxItems': 3,
            },
        }

    def map_serializer(self, field: BaseSerializer) -> OpenAPISchema:
        if isinstance(field, ListSerializer):
            return array_schema(self.view_schema.map_serializer(field.child))
        else:
            schema = self.view_schema.map_serializer(field)
            schema['type'] = 'object'
            return schema

    def map_related(
        self, field: typing.Union[ManyRelatedField, PrimaryKeyRelatedField]
    ) -> typing.Optional[OpenAPISchema]:
        if isinstance(field, ManyRelatedField):
            return array_schema(self.map_field(field.child_relation))
        if isinstance(field, PrimaryKeyRelatedField):
            model = getattr(field.queryset, 'model', None)
            if model is not None:
                model_field = model._meta.pk
                if isinstance(model_field, AutoField):
                    return {'type': 'integer'}

    def map_list_field(self, field: ListField) -> OpenAPISchema:
        return array_schema(self.map_field(field.child))

    def map_decimal_field(self, field: DecimalField) -> OpenAPISchema:
        if getattr(field, 'coerce_to_string', api_settings.COERCE_DECIMAL_TO_STRING):
            schema = string_schema('decimal')
        else:
            schema = {'type': 'number'}

        if field.decimal_places:
            schema['multipleOf'] = float('.' + (field.decimal_places - 1) * '0' + '1')
        if field.max_whole_digits:
            value = int(field.max_whole_digits * '9') + 1
            schema['maximum'] = value
            schema['minimum'] = -value

        if field.max_value:
            schema['maximum'] = field.max_value
        if field.min_value:
            schema['minimum'] = field.min_value

        return schema

    def map_numeric_field(self, field: Field) -> OpenAPISchema:
        schema = {'type': 'number'}
        if field.max_value:
            schema['maximum'] = field.max_value
        if field.min_value:
            schema['minimum'] = field.min_value

        if isinstance(field, IntegerField):
            schema = {'type': 'integer'}
            max_value = int(field.max_value or 0)
            min_value = int(field.min_value or 0)
            if max(max_value, min_value) > 2147483647:
                schema['format'] = 'int64'

        return schema

    def map_ipaddress_field(self, field: IPAddressField) -> OpenAPISchema:
        string_format = field.protocol if field.protocol != 'both' else None
        return string_schema(string_format)

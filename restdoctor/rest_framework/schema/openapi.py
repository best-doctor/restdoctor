from __future__ import annotations

import contextlib
import logging
import typing

from django.conf import settings
from django.core.exceptions import FieldDoesNotExist, ImproperlyConfigured
from django.db import models
from django.utils.module_loading import import_string
from django_filters import Filter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework.fields import Field
from rest_framework.pagination import BasePagination
from rest_framework.schemas.openapi import AutoSchema
from rest_framework.schemas.utils import is_list_view
from rest_framework.serializers import BaseSerializer

from restdoctor.rest_framework.pagination.mixins import SerializerClassPaginationMixin
from restdoctor.rest_framework.schema.custom_types import SchemaGenerator, ViewSchemaBase
from restdoctor.rest_framework.schema.fields import FieldSchema
from restdoctor.rest_framework.schema.filters import get_filter_schema
from restdoctor.rest_framework.schema.serializers import SerializerSchema
from restdoctor.rest_framework.schema.utils import (
    get_action,
    get_action_code_schemas_from_map,
    get_action_map_kwargs,
    get_app_prefix,
    normalize_action_schema,
)
from restdoctor.rest_framework.serializers import EmptySerializer
from restdoctor.rest_framework.views import SerializerClassMapApiView

if typing.TYPE_CHECKING:
    from restdoctor.rest_framework.schema.custom_types import (
        CodeActionSchemaTuple,
        CodeDescriptionTuple,
        OpenAPISchema,
        OpenAPISchemaParameter,
    )

log = logging.getLogger(__name__)


class RestDoctorSchema(ViewSchemaBase, AutoSchema):
    filter_map = import_string(settings.API_SCHEMA_FILTER_MAP_PATH)
    methods_with_request_body = {'PUT', 'PATCH', 'POST'}
    methods_with_request_serializer_filter = {'GET'}

    def __init__(
        self, generator: SchemaGenerator = None, *args: typing.Any, **kwargs: typing.Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.generator = generator
        self.field_schema = FieldSchema(self)
        self.serializer_schema = SerializerSchema(self)

    def map_renderers(self, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        if self.generator:
            return [self.generator.get_content_type(resource=None, api_format=None)]

        vendor = settings.API_VENDOR_STRING.lower()
        media_types = [f'application/vnd.{vendor}']
        return media_types

    def merge_parameters(
        self,
        path: str,
        parameters: list[OpenAPISchemaParameter],
        serializer_parameters: list[OpenAPISchemaParameter],
    ) -> list[OpenAPISchemaParameter]:
        original_parameters = {
            parameter['name']: parameter_index
            for parameter_index, parameter in enumerate(parameters)
        }
        for serializer_parameter in serializer_parameters:
            if serializer_parameter['name'] in original_parameters:
                if settings.API_SCHEMA_PRIORITIZE_SERIALIZER_PARAMETERS:
                    parameters.pop(original_parameters[serializer_parameter['name']])
                    parameters.append(serializer_parameter)
                else:
                    log.warning(
                        f'Serializer at path {path} shadows parameter '
                        f'"{serializer_parameter["name"]}". '
                        f'Turn on API_SCHEMA_PRIORITIZE_SERIALIZER_PARAMETERS to use serializer '
                        f'parameter for schema.'
                    )
            else:
                parameters.append(serializer_parameter)

        return parameters

    def get_operation(self, path: str, method: str) -> OpenAPISchema:
        operation = super().get_operation(path, method)
        operation['parameters'] = self.merge_parameters(
            path,
            operation['parameters'],
            self.get_request_serializer_filter_parameters(path, method),
        )
        operation['tags'] = self.get_tags(path, method)

        return operation

    def get_filter_parameters(self, path: str, method: str) -> typing.List[OpenAPISchema]:
        if not self.allows_filters(path, method):
            return []
        parameters = []
        for filter_backend in self.view.filter_backends:
            if issubclass(filter_backend, DjangoFilterBackend):
                parameters += self.get_django_filter_schema_operation_parameters(filter_backend())
            else:
                parameters += filter_backend().get_schema_operation_parameters(self.view)
        return parameters

    def allows_filters(self, path: str, method: str) -> bool:
        if settings.API_IGNORE_FILTER_PARAMS_FOR_DETAIL and not is_list_view(
            path, method, self.view
        ):
            return False
        return super().allows_filters(path, method)

    def allows_request_serializer_filter(self, path: str, method: str) -> bool:
        methods_with_request_serializer_filter = set(
            getattr(
                self.view,
                'schema_methods_with_request_serializer_filter',
                self.methods_with_request_serializer_filter,
            )
        )
        return method in methods_with_request_serializer_filter

    def get_request_serializer_filter_parameters(
        self, path: str, method: str
    ) -> typing.List[OpenAPISchema]:
        if not self.allows_request_serializer_filter(path, method):
            return []
        parameters = []
        request_serializer_class = self.view.get_request_serializer_class(use_default=False)
        request_serializer = request_serializer_class()
        if not isinstance(request_serializer, EmptySerializer):
            for field in request_serializer.fields.values():
                field_schema = self.field_schema.get_field_schema(field)
                parameters.append(
                    {
                        'name': field.field_name,
                        'required': field.required,
                        'in': 'query',
                        'schema': field_schema,
                    }
                )
        return parameters

    def get_action_name(self, path: str, method: str) -> str:
        action = get_action(path, method, self.view)
        if is_list_view(path, method, self.view):
            return 'list'
        elif action not in self.method_mapping:
            return action.lower()
        else:
            return self.method_mapping[method.lower()].lower()

    def get_object_name_by_view_class_name(
        self, clean_suffixes: typing.Sequence[str] = None
    ) -> str:
        clean_suffixes = clean_suffixes or []
        object_name = self.view.__class__.__name__
        for suffix in sorted(clean_suffixes, key=len, reverse=True):
            if object_name.endswith(suffix):
                object_name = object_name[: -len(suffix)]
                break
        return object_name

    def get_object_name(self, path: str, method: str, action_name: str) -> str:
        action = get_action(path, method, self.view)

        # Try to deduce the ID from the view's model
        model = getattr(getattr(self.view, 'queryset', None), 'model', None)
        if model is not None:
            return model.__name__

        # Try with the serializer class name
        if isinstance(self.view, SerializerClassMapApiView):
            serializer_class = self.view.get_serializer_class('response', action)
            if serializer_class:
                object_name = serializer_class.__name__
                if object_name.endswith('Serializer'):
                    object_name = object_name[:-10]
                return object_name

        object_name = self.get_object_name_by_view_class_name(
            clean_suffixes=['APIView', 'View', 'ViewSet']
        )

        # Due to camel-casing of classes and `action` being lowercase, apply title in order to find if action truly
        # comes at the end of the name
        if object_name.endswith(action_name.title()):  # ListView, UpdateAPIView, ThingDelete ...
            object_name = object_name[: -len(action_name)]

        return object_name

    def get_operation_id(self, path: str, method: str) -> str:
        action_name = self.get_action_name(path, method)

        schema_operation_id_map = getattr(self.view, 'schema_operation_id_map', None)
        if schema_operation_id_map and action_name in schema_operation_id_map:
            return schema_operation_id_map[action_name]

        object_name = self.get_object_name(path, method, action_name)

        if action_name == 'list' and not object_name.endswith(
            's'
        ):  # listThings instead of listThing
            object_name += 's'

        if settings.USE_APP_PREFIX_FOR_SCHEMA_OPERATION_IDS:
            app_prefix = get_app_prefix(module_path=self.view.__module__)
            return f'{app_prefix}__{action_name}__{object_name}'

        return action_name + object_name

    def get_pagination_parameters(self, path: str, method: str) -> typing.List[OpenAPISchema]:
        if not is_list_view(path, method, self.view):
            return []

        paginator: BasePagination = self.get_paginator()
        if not paginator:
            return []

        if isinstance(paginator, SerializerClassPaginationMixin):
            serializer_class = paginator.get_request_serializer_class()
        else:
            serializer_class = getattr(paginator, 'serializer_class', None)  # type: ignore
        if serializer_class:
            return self.serializer_schema.map_query_serializer(serializer_class())
        return paginator.get_schema_operation_parameters(self.view)

    def get_serializer(
        self, path: str, method: str, stage: str, api_format: str = None
    ) -> typing.Optional[BaseSerializer]:
        view = self.view
        action = get_action(path, method, view)

        serializer_class = None
        if issubclass(view.__class__, SerializerClassMapApiView):
            serializer_class = view.get_serializer_class(stage, action, api_format)

        if serializer_class is None:
            serializer = view.get_serializer()
        else:
            serializer = serializer_class()

        return serializer

    def get_request_body_schema(
        self, path: str, method: str, api_format: str = None
    ) -> OpenAPISchema:
        serializer = self.get_serializer(path, method, 'request', api_format=api_format)

        if serializer is None:
            return {}

        return self.map_serializer(serializer, read_only=False, required=(method != 'PATCH'))

    def is_method_with_request_body(self, method: str) -> bool:
        methods_with_request_body = set(
            getattr(self.view, 'schema_methods_with_request_body', self.methods_with_request_body)
        )
        return method in methods_with_request_body

    def get_request_body(self, path: str, method: str) -> OpenAPISchema:
        if not self.is_method_with_request_body(method):
            return {}

        self.request_media_types = self.map_parsers(path, method)
        schema = self.get_request_body_schema(path, method)

        return {'content': {ct: {'schema': schema} for ct in self.request_media_types}}

    def get_item_schema(
        self, path: str, method: str, api_format: str = None
    ) -> typing.Optional[OpenAPISchema]:
        serializer = self.get_serializer(path, method, 'response', api_format=api_format)

        if serializer is None:
            return None

        return self.serializer_schema.map_serializer(serializer, write_only=False)

    def get_content_schema(
        self, response_schema: OpenAPISchema, description: str = ''
    ) -> OpenAPISchema:
        content_schema: OpenAPISchema = {'description': description}
        if response_schema:
            content_schema['content'] = {
                content_type: {'schema': response_schema}
                for content_type in self.response_media_types
            }
        return content_schema

    def get_response_schema(self, path: str, method: str, api_format: str = None) -> OpenAPISchema:
        response_schema: OpenAPISchema = {'type': 'object', 'properties': {}}

        item_schema = self.get_item_schema(path, method, api_format)

        if is_list_view(path, method, self.view):
            response_schema['properties']['data'] = {'type': 'array', 'items': item_schema}
            paginator = self.get_paginator()
            if paginator:
                response_schema = paginator.get_paginated_response_schema(response_schema)
            meta_schema = self.get_meta_schema(path, method, api_format)
            if response_schema['properties'].get('meta'):
                response_schema = self.update_meta_schema(response_schema, meta_schema)
            else:
                response_schema['properties']['meta'] = meta_schema
        else:
            response_schema['properties']['data'] = item_schema

        return response_schema

    def get_paginator(self) -> typing.Optional[BasePagination]:
        pagination_class = getattr(self.view, 'pagination_class', None)
        if pagination_class:
            return pagination_class(view_schema=self)
        return None

    def update_meta_schema(
        self, response_schema: OpenAPISchema, meta_schema: typing.Optional[OpenAPISchema]
    ) -> OpenAPISchema:
        if not meta_schema:
            return response_schema
        for name, value in response_schema['properties']['meta'].items():
            with contextlib.suppress(KeyError):
                data = meta_schema[name]
                if isinstance(value, list):
                    value.append(data)
                if isinstance(value, dict):
                    value.update(data)
        return response_schema

    def get_meta_schema(
        self, path: str, method: str, api_format: str = None
    ) -> typing.Optional[OpenAPISchema]:
        if issubclass(self.view.__class__, SerializerClassMapApiView):
            action = get_action(path, method, self.view)
            serializer_class = self.view.get_serializer_class(
                'meta', action, api_format, use_default=False
            )

            if serializer_class is None:
                return None
            serializer = serializer_class()
            return self.get_serializer_schema(serializer)

    def get_action_code_description(self, path: str, method: str) -> CodeDescriptionTuple:
        for code, description, _ in self.get_action_code_schemas(path, method):
            if code < '400':
                return code, description
        return '200', 'Успешный запрос.'

    def get_action_code_schemas(
        self, path: str, method: str
    ) -> typing.Iterator[CodeActionSchemaTuple]:
        success_codes_seen: typing.Set[str] = set()
        error_codes_seen: typing.Set[str] = set()
        action = get_action(path, method, self.view)
        kwargs_variants = get_action_map_kwargs(
            action, getattr(self.view, 'schema_action_codes_map', None)
        )

        for kwargs_variant in kwargs_variants:
            for code, action_schema in get_action_code_schemas_from_map(*kwargs_variant):
                if code > '400':
                    codes_seen_set = error_codes_seen
                else:
                    codes_seen_set = success_codes_seen
                if code not in codes_seen_set:
                    codes_seen_set.add(code)
                    if action_schema is not None:
                        yield normalize_action_schema(code, action_schema)

    def get_content_schema_by_type(self, path: str, method: str, schema_type: str) -> OpenAPISchema:
        if schema_type == 'responses':
            schema_method_name = 'get_response_schema'
        else:
            schema_method_name = 'get_request_body_schema'

        return self.get_versioned_content_schema(path, method, schema_method_name)

    def get_versioned_content_schema(
        self, path: str, method: str, schema_method_name: str
    ) -> OpenAPISchema:
        if not self.generator:
            return self.get_default_content_schema(path, method, schema_method_name)

        generator = self.generator
        content_schema: OpenAPISchema = {}

        schema_method = getattr(self, schema_method_name)

        default_schema = schema_method(path, method)
        content_type = generator.get_content_type(resource=None, api_format=None)
        content_schema[content_type] = {'schema': default_schema}

        schema_method = getattr(self.view.schema, schema_method_name)

        for api_format in self.generator.api_formats:
            if api_format != self.generator.api_default_format:
                resource_schema = schema_method(path, method, api_format=api_format)
                if resource_schema != default_schema:
                    content_type = generator.get_content_type(resource=None, api_format=api_format)
                    content_schema[content_type] = {'schema': resource_schema}

        return content_schema

    def get_default_content_schema(
        self, path: str, method: str, schema_method_name: str
    ) -> OpenAPISchema:
        content_schema = {}

        vendor = settings.API_VENDOR_STRING.lower()
        default_content_type = f'application/vnd.{vendor}'

        schema_method = getattr(self, schema_method_name)

        default_schema = schema_method(path, method)

        content_schema[default_content_type] = {'schema': default_schema}

        return content_schema

    def get_responses(self, path: str, method: str) -> OpenAPISchema:
        schema: OpenAPISchema = {}
        self.response_media_types = self.map_renderers(path, method)

        for code, description, action_schema in self.get_action_code_schemas(path, method):
            if action_schema is None:
                schema[code] = {
                    'description': description,
                    'content': self.get_content_schema_by_type(path, method, 'responses'),
                }
            else:
                if '$ref' not in action_schema or self.generator:
                    schema[code] = self.get_content_schema(action_schema, description=description)

        return schema

    def get_tags(self, path: str, method: str) -> typing.List[str]:
        view = self.view

        schema_tags = getattr(view, 'schema_tags', [])
        if schema_tags:
            return view.schema_tags

        schema_tags = getattr(self, '_tags', [])
        if schema_tags:
            return view.schema_tags

        # First element of a specific path could be valid tag. This is a fallback solution.
        # PUT, PATCH, GET(Retrieve), DELETE:        /user_profile/{id}/       tags = [user-profile]
        # POST, GET(List):                          /user_profile/            tags = [user-profile]
        if path.startswith('/'):
            path = path[1:]

        return [path.split('/')[0].replace('_', '-')]

    def get_view_queryset(self) -> models.QuerySet | None:
        try:
            return self.view.get_queryset()
        except Exception:
            return None

    def get_django_filter_schema_operation_parameters(
        self, filter_backend: DjangoFilterBackend
    ) -> typing.List[OpenAPISchema]:
        queryset = self.get_view_queryset()

        filterset_class = filter_backend.get_filterset_class(self.view, queryset)

        if not filterset_class:
            return []

        parameters = []
        for field_name, field in filterset_class.base_filters.items():
            parameter = {
                'name': field_name,
                'required': field.extra['required'],
                'in': 'query',
                'description': self.get_verbose_filter_field_description(filterset_class, field),
                'schema': get_filter_schema(filter_field=field, filter_map=self.filter_map),
            }
            parameters.append(parameter)
        return parameters

    def get_verbose_filter_field_description(
        self, filterset_class: FilterSet, field: Filter
    ) -> str:
        if field.label:
            return field.label

        description = self.try_get_field_verbose_name(filterset_class._meta.model, field.field_name)

        if not description and settings.API_STRICT_SCHEMA_VALIDATION:
            raise ImproperlyConfigured(
                f'Field {field.field_name} in {filterset_class.__name__} '
                f'should have "label" argument or "verbose_name" in source model field'
            )

        return str(description or field.field_name)

    def try_get_field_verbose_name(
        self, model: models.Model, full_field_name: str
    ) -> typing.Optional[str]:
        field_parts = full_field_name.split('__')
        path_to_field = field_parts[:-1]
        field_name = field_parts[-1]
        with contextlib.suppress(AttributeError, LookupError, FieldDoesNotExist):
            for part in path_to_field:
                model = model._meta.get_field(part).related_model

            field = model._meta.get_field(field_name)
            if field.is_relation:
                return field.related_model._meta.verbose_name
            else:
                return field.verbose_name

    def _get_action_name(self, path: str, method: str) -> str:
        return self.get_action_name(path, method)

    def _get_object_name_by_view_class_name(
        self, clean_suffixes: typing.Sequence[str] = None
    ) -> str:
        return self.get_object_name_by_view_class_name(clean_suffixes=clean_suffixes)

    def _get_object_name(self, path: str, method: str, action_name: str) -> str:
        return self.get_object_name(path, method, action_name)

    def _get_operation_id(self, path: str, method: str) -> str:
        return self.get_operation_id(path, method)

    def _get_pagination_parameters(self, path: str, method: str) -> typing.List[OpenAPISchema]:
        return self.get_pagination_parameters(path, method)

    def _get_serializer(
        self, path: str, method: str, stage: str, api_format: str = None
    ) -> typing.Optional[BaseSerializer]:
        return self.get_serializer(path, method, stage, api_format=api_format)

    def _get_request_body_schema(
        self, path: str, method: str, api_format: str = None
    ) -> OpenAPISchema:
        return self.get_request_body_schema(path, method, api_format=api_format)

    def _get_request_body(self, path: str, method: str) -> OpenAPISchema:
        return self.get_request_body(path, method)

    def _get_item_schema(
        self, path: str, method: str, api_format: str = None
    ) -> typing.Optional[OpenAPISchema]:
        return self.get_item_schema(path, method, api_format=api_format)

    def _get_content_schema(
        self, response_schema: OpenAPISchema, description: str = ''
    ) -> OpenAPISchema:
        return self.get_content_schema(response_schema, description=description)

    def _get_response_schema(self, path: str, method: str, api_format: str = None) -> OpenAPISchema:
        return self.get_response_schema(path, method, api_format=api_format)

    def _get_action_code_description(self, path: str, method: str) -> CodeDescriptionTuple:
        return self.get_action_code_description(path, method)

    def _get_responses(self, path: str, method: str) -> OpenAPISchema:
        return self.get_responses(path, method)

    def _map_field(self, field: Field) -> typing.Optional[OpenAPISchema]:
        return self.field_schema.map_field(field)

    def _get_field_description(self, field: Field) -> typing.Optional[str]:
        return self.field_schema.get_field_description(field)

    def _get_field_schema(self, field: Field) -> OpenAPISchema:
        return self.field_schema.get_field_schema(field)

    def _get_serializer_schema(
        self,
        serializer: BaseSerializer,
        write_only: bool = True,
        read_only: bool = True,
        required: bool = True,
    ) -> OpenAPISchema:
        return self.serializer_schema.get_serializer_schema(
            serializer, write_only=write_only, read_only=read_only, required=required
        )

    def _map_serializer(
        self,
        serializer: BaseSerializer,
        write_only: bool = True,
        read_only: bool = True,
        required: bool = True,
    ) -> OpenAPISchema:
        return self.serializer_schema.map_serializer(
            serializer, write_only=write_only, read_only=read_only, required=required
        )

    def _map_query_serializer(self, serializer: BaseSerializer) -> typing.List[OpenAPISchema]:
        return self.serializer_schema.map_query_serializer(serializer)

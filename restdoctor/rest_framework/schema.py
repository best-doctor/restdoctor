from __future__ import annotations

import functools
import typing
from urllib.parse import urljoin

from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.utils.encoding import force_str
from rest_framework.fields import Field, empty, HiddenField, SerializerMethodField
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.schemas.openapi import AutoSchema, SchemaGenerator
from rest_framework.schemas.utils import is_list_view
from rest_framework.serializers import BaseSerializer, ModelSerializer, ModelField

from restdoctor.rest_framework.views import SerializerClassMapApiView

if typing.TYPE_CHECKING:
    from restdoctor.rest_framework.custom_types import (
        ActionCodesMap, LocalRefs, OpenAPISchema, Handler, CodesTuple, ResourceHandlersMap,
    )


# True и False - относится ли action к коллекции или отдельному элементу
ACTIONS_MAP = {
    True: {'get': 'list', 'post': 'create'},
    False: {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'},
}

ACTION_CODES_MAP: ActionCodesMap = {
    'list': ('200', 'Успешный запрос коллекции.'),
    'retrieve': ('200', 'Успешный запрос объекта.'),
    'update': ('200', 'Успешное изменение объекта.'),
    'partial_update': ('200', 'Успешное изменение объекта.'),
    'create': ('201', 'Успешное создание объекта.'),
    'destroy': ('204', 'Успешное удаление объекта.'),
}

ERROR_CODES = (
    ('400', {'$ref': '#/components/schemas/ErrorResponseSchema'}, 'Ошибка валидации запроса.'),
    ('404', {'$ref': '#/components/schemas/NotFoundResponseSchema'}, 'Ресурс не найден.'),
)


@functools.lru_cache()
def get_action(path: str, method: str, view: GenericAPIView) -> str:
    action = getattr(view, 'action', None)
    if action:
        return action
    action_map = getattr(view, 'action_map', None) or {}
    method_name = method.lower()
    return action_map.get(method_name, method_name)


class SchemaWrapper(Field):
    def __new__(
        cls, wrapped: Field, schema_type: typing.Union[Field, typing.Type[Field]] = None,
    ) -> Field:
        if isinstance(schema_type, type):
            schema_type = schema_type()
        wrapped.schema_type = schema_type
        return wrapped


class LocalRefsRegistry:
    def __init__(self) -> None:
        self._local_refs: LocalRefs = {}

    def put_local_ref(self, ref: str, schema: OpenAPISchema) -> None:
        if ref.startswith('#/components'):
            path = tuple(ref.split('/')[2:])
            self._local_refs[path] = schema

    def get_components(self) -> OpenAPISchema:
        components: OpenAPISchema = {}
        for path, schema in self._local_refs.items():
            component = components
            for path_item in path[:-1]:
                try:
                    component = component[path_item]
                except KeyError:
                    components[path_item] = {}
                    component = component[path_item]
            component[path[-1]] = schema
        return components


class RefsSchemaGenerator(SchemaGenerator):
    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.local_refs_registry = LocalRefsRegistry()

        self.api_version = settings.API_DEFAULT_VERSION
        urlconf = kwargs.get('urlconf')
        if urlconf:
            for api_version, api_urlconf in settings.API_VERSIONS.items():
                if api_urlconf == urlconf:
                    self.api_version = api_version
                    break
        self.api_default_format = settings.API_DEFAULT_FORMAT
        self.api_formats = settings.API_FORMATS

    def get_paths(self, request: Request = None) -> typing.Optional[OpenAPISchema]:
        result: OpenAPISchema = {}

        paths, view_endpoints = self._get_paths_and_endpoints(request)

        if not paths:
            return None

        for path, method, view in view_endpoints:
            if not self.has_view_permissions(path, method, view):
                continue
            operation = view.schema.get_operation(path, method)
            if path.startswith('/'):
                path = path[1:]
            path = urljoin(self.url or '/', path)

            result.setdefault(path, {})
            result[path][method.lower()] = operation

        return result

    def create_view(self, callback: Handler, method: str, request: Request = None) -> GenericAPIView:
        view = super().create_view(callback, method, request)
        view_class = getattr(view, 'schema_class', RestDoctorSchema)
        view.schema = view_class(generator=self)
        return view

    def get_error_schema(self, description: str = 'Описание ошибки', detailed: bool = False) -> OpenAPISchema:
        schema: OpenAPISchema = {
            'type': 'object',
            'properties': {
                'message': {
                    'type': 'string',
                    'description': description,
                },
            },
        }
        if detailed:
            schema['properties']['errors'] = {
                'type': 'array',
                'item': {
                    'type': 'object',
                },
            }
        return schema

    def get_schema(self, request: Request = None, public: bool = False) -> typing.Optional[OpenAPISchema]:
        self._initialise_endpoints()
        self.local_refs_registry.put_local_ref(
            '#/components/schemas/ErrorResponseSchemaDetailed',
            self.get_error_schema(detailed=True),
        )
        self.local_refs_registry.put_local_ref(
            '#/components/schemas/ErrorResponseSchema',
            self.get_error_schema(),
        )
        self.local_refs_registry.put_local_ref(
            '#/components/schemas/NotFoundResponseSchema',
            self.get_error_schema(description='Ресурс не найден.'),
        )

        paths = self.get_paths(None if public else request)
        if not paths:
            return None

        schema = {
            'openapi': '3.0.2',
            'info': self.get_info(),
            'paths': paths,
        }
        components = self.local_refs_registry.get_components()
        if components:
            schema['components'] = components

        return schema


class RestDoctorSchema(AutoSchema):
    def __init__(self, generator: SchemaGenerator = None, *args: typing.Any, **kwargs: typing.Any) -> None:
        super().__init__(*args, **kwargs)
        self.generator = generator

    def map_renderers(self, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        media_types = ['application/vnd.bestdoctor']
        return media_types

    def get_operation(self, path: str, method: str) -> OpenAPISchema:
        view = self.view

        operation = super().get_operation(path, method)

        schema_tags = getattr(view, 'schema_tags', [])
        if schema_tags:
            operation['tags'] = view.schema_tags
        return operation

    def _get_action_name(self, path: str, method: str) -> str:
        action = get_action(path, method, self.view)
        if is_list_view(path, method, self.view):
            return 'list'
        elif action not in self.method_mapping:
            return action
        else:
            return self.method_mapping[method.lower()]

    def _get_object_name_by_view_class_name(self, clean_suffixes: typing.Sequence[str] = None) -> str:
        clean_suffixes = clean_suffixes or []
        object_name = self.view.__class__.__name__
        for suffix in sorted(clean_suffixes, key=len, reverse=True):
            if object_name.endswith(suffix):
                object_name = object_name[:-len(suffix)]
                break
        return object_name

    def _get_object_name(self, path: str, method: str, action_name: str) -> str:
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

        object_name = self._get_object_name_by_view_class_name(
            clean_suffixes=['APIView', 'View', 'ViewSet'])

        # Due to camel-casing of classes and `action` being lowercase, apply title in order to find if action truly
        # comes at the end of the name
        if object_name.endswith(action_name.title()):  # ListView, UpdateAPIView, ThingDelete ...
            object_name = object_name[:-len(action_name)]

        return object_name

    def _get_operation_id(self, path: str, method: str) -> str:
        action_name = self._get_action_name(path, method)
        object_name = self._get_object_name(path, method, action_name)

        if action_name == 'list' and not object_name.endswith('s'):  # listThings instead of listThing
            object_name += 's'

        return action_name + object_name

    def _get_pagination_parameters(self, path: str, method: str) -> typing.List[OpenAPISchema]:
        if not is_list_view(path, method, self.view):
            return []

        paginator = self._get_paginator()
        if not paginator:
            return []

        serializer_class = getattr(paginator, 'serializer_class', None)
        if serializer_class:
            return self._map_query_serializer(serializer_class())
        return paginator.get_schema_operation_parameters(self.view)

    def _get_serializer(
        self, path: str, method: str, stage: str, api_format: str = None,
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

    def _get_request_body_schema(self, path: str, method: str) -> OpenAPISchema:
        serializer = self._get_serializer(path, method, 'request')

        if serializer is None:
            return {}

        return self._map_serializer(serializer, read_only=False, required=(method != 'PATCH'))

    def _get_request_body(self, path: str, method: str) -> OpenAPISchema:
        if method not in ('PUT', 'PATCH', 'POST'):
            return {}

        self.request_media_types = self.map_parsers(path, method)
        schema = self._get_request_body_schema(path, method)

        return {
            'content': {
                ct: {'schema': schema}
                for ct in self.request_media_types
            },
        }

    def _get_item_schema(self, path: str, method: str, api_format: str = None) -> typing.Optional[OpenAPISchema]:
        serializer = self._get_serializer(path, method, 'response', api_format=api_format)

        if serializer is None:
            return None

        return self._map_serializer(serializer, write_only=False)

    def _get_content_schema(self, response_schema: OpenAPISchema, description: str = '') -> OpenAPISchema:
        return {
            'content': {
                content_type: {'schema': response_schema}
                for content_type in self.response_media_types
            },
            'description': description,
        }

    def _get_response_schema(self, path: str, method: str, api_format: str = None) -> OpenAPISchema:
        response_schema: OpenAPISchema = {
            'type': 'object',
            'properties': {},
        }

        item_schema = self._get_item_schema(path, method, api_format)

        if is_list_view(path, method, self.view):
            response_schema['properties']['data'] = {
                'type': 'array',
                'items': item_schema,
            }
            paginator = self._get_paginator()
            if paginator:
                response_schema = paginator.get_paginated_response_schema(response_schema)
        else:
            response_schema['properties']['data'] = item_schema

        return response_schema

    def _get_action_code_description(self, path: str, method: str) -> CodesTuple:
        action = get_action(path, method, self.view)
        schema_action_codes_map: ActionCodesMap = getattr(self.view, 'schema_action_codes_map', None)
        code = ''
        if schema_action_codes_map:
            code, description = schema_action_codes_map.get(action, ('', ''))
        if not code:
            code, description = ACTION_CODES_MAP.get(action, ('200', 'Успешный запрос.'))
        return code, description

    def _get_responses(self, path: str, method: str) -> OpenAPISchema:
        code, description = self._get_action_code_description(path, method)

        if method == 'DELETE':
            return {code: {'description': description}}

        self.response_media_types = self.map_renderers(path, method)

        schema: OpenAPISchema = {code: {}}

        default_response_schema = self._get_response_schema(path, method)
        schema[code].update(self._get_content_schema(default_response_schema, description=description))

        if self.generator:
            default_content_type = self.response_media_types[0]

            for api_format in self.generator.api_formats:
                if api_format != self.generator.api_default_format:
                    response_schema = self._get_response_schema(path, method, api_format)
                    if response_schema != default_response_schema:
                        content_type = f'{default_content_type}.{api_format}'
                        schema[code]['content'][content_type] = {'schema': response_schema}

            for code, error_schema, description in ERROR_CODES:
                schema[code] = self._get_content_schema(error_schema, description=description)

        return schema

    def _map_field(self, field: Field) -> OpenAPISchema:
        # Field.__deepcopy__ сбрасывает кастомные атрибуты, поэтому схему ищем через класс сериализатора
        if isinstance(field, SerializerMethodField):
            parent_field = field.parent.__class__._declared_fields[field.field_name]
            field = getattr(parent_field, 'schema_type', field)

        return super()._map_field(field)

    def _get_field_description(self, field: Field) -> typing.Optional[str]:
        if field.help_text:
            return str(field.help_text)
        elif isinstance(field.parent, ModelSerializer):
            if isinstance(field, ModelField):
                return field.model_field.verbose_name
            elif field.source != '*':
                try:
                    return str(field.parent.Meta.model._meta.get_field(field.source).verbose_name)
                except (AttributeError, LookupError, FieldDoesNotExist):
                    pass

    def _get_field_schema(self, field: Field) -> OpenAPISchema:
        schema = self._map_field(field)
        if field.read_only:
            schema['readOnly'] = True
        if field.write_only:
            schema['writeOnly'] = True
        if field.allow_null:
            schema['nullable'] = True
        if field.default and field.default != empty and not callable(field.default):
            schema['default'] = field.default
        description = self._get_field_description(field)
        if description:
            schema['description'] = description

        self._map_field_validators(field, schema)

        return schema

    def _get_serializer_schema(
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

            properties[field.field_name] = self._get_field_schema(field)

        schema: OpenAPISchema = {
            'type': 'object',
            'properties': properties,
        }
        if serializer.__doc__:
            schema['description'] = serializer.__doc__
        if required and required_list:
            schema['required'] = required_list
        return schema

    def _map_serializer(
        self, serializer: BaseSerializer,
        write_only: bool = True, read_only: bool = True, required: bool = True,
    ) -> OpenAPISchema:
        schema = self._get_serializer_schema(
            serializer, write_only=write_only, read_only=read_only, required=required)

        if self.generator:
            serializer_class_name = serializer.__class__.__name__
            if serializer_class_name.endswith('Serializer'):
                serializer_class_name = serializer_class_name[:-10]
            ref = f'#/components/schemas/{serializer_class_name}'
            self.generator.local_refs_registry.put_local_ref(ref, schema)
            schema = {'$ref': ref}

        return schema

    def _map_query_serializer(self, serializer: BaseSerializer) -> typing.List[OpenAPISchema]:
        props = []

        for field in serializer.fields.values():
            if isinstance(field, HiddenField):
                continue

            prop = {
                'name': field.field_name,
                'in': 'query',
                'required': field.required,
                'schema': self._get_field_schema(field),
            }

            if field.help_text:
                prop['description'] = force_str(field.help_text)

            props.append(prop)

        return props


class ResourceSchema(RestDoctorSchema):
    def _get_object_name(self, path: str, method: str, action_name: str) -> str:
        return self._get_object_name_by_view_class_name(
            clean_suffixes=['View', 'APIView', 'ViewSet'])

    def _get_resources(self, method: str) -> ResourceHandlersMap:
        return {
            resource: handler for resource, handler in self.view.resource_handlers_map.items()
            if (
                method in self.view.resource_discriminate_methods
                or resource == self.view.default_discriminative_value
            )
        }

    def __get_item_schema(self, path: str, method: str, api_format: str = None) -> typing.Optional[OpenAPISchema]:
        schemas = {}
        if self.generator:
            for resource, handler in self._get_resources(method).items():
                view = self.generator.create_view(handler, method, request=self.view.request)
                schemas[resource] = view.schema._get_item_schema(path, method, api_format=api_format)

        list_schemas = list(schemas.values())
        if len(list_schemas) == 1:
            return list_schemas[0]
        return {'oneOf': list_schemas}

    def _get_request_body_schema(self, path: str, method: str) -> OpenAPISchema:
        schemas = {}
        if self.generator:
            for resource, handler in self._get_resources(method).items():
                view = self.generator.create_view(handler, method, request=self.view.request)
                schemas[resource] = view.schema._get_request_body_schema(path, method)

        list_schemas = list(schemas.values())
        if len(list_schemas) == 1:
            return list_schemas[0]
        return {'oneOf': list_schemas}

    def _get_response_schema(self, path: str, method: str, api_format: str = None) -> OpenAPISchema:
        schemas = {}
        if self.generator:
            for resource, handler in self._get_resources(method).items():
                view = self.generator.create_view(handler, method, request=self.view.request)
                schemas[resource] = view.schema._get_response_schema(path, method, api_format=api_format)

        list_schemas = list(schemas.values())
        if len(list_schemas) == 1:
            return list_schemas[0]
        return {'oneOf': list_schemas}

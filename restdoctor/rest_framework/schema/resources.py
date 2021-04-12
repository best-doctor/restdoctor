from __future__ import annotations

import typing

from django.conf import settings

from restdoctor.rest_framework.schema.openapi import RestDoctorSchema
from restdoctor.rest_framework.schema.utils import get_action

if typing.TYPE_CHECKING:
    from restdoctor.rest_framework.custom_types import Handler, ResourceHandlersMap
    from restdoctor.rest_framework.generics import GenericAPIView
    from restdoctor.rest_framework.schema.custom_types import CodeActionSchemaTuple, OpenAPISchema


def get_single_or_default_handler(view: GenericAPIView) -> typing.Optional[Handler]:
    keys = list(view.resource_handlers_map.keys())
    if len(keys) == 1:
        return view.resource_handlers_map[keys[0]]
    return view.resource_handlers_map.get(view.default_discriminative_value)


class ResourceSchema(RestDoctorSchema):
    def get_object_name(self, path: str, method: str, action_name: str) -> str:
        return self.get_object_name_by_view_class_name(
            clean_suffixes=['View', 'APIView', 'ViewSet']
        )

    def get_action_code_schemas(
        self, path: str, method: str
    ) -> typing.Iterator[CodeActionSchemaTuple]:
        codes_seen: typing.Set[str] = set()

        if self.generator:
            for _, handler in self.get_resources(method).items():
                view = self.generator.create_view(handler, method, request=self.view.request)
                for code, serializer, schema in view.schema.get_action_code_schemas(path, method):
                    if code not in codes_seen:
                        yield code, serializer, schema

    def get_resources(self, method: str) -> ResourceHandlersMap:
        return {
            resource: handler
            for resource, handler in self.view.resource_handlers_map.items()
            if (
                method in self.view.resource_discriminate_methods
                or resource == self.view.default_discriminative_value
            )
        }

    def get_resources_request_body_schema(self, path: str, method: str) -> OpenAPISchema:
        schemas = {}
        if self.generator:
            for resource, handler in self.get_resources(method).items():
                view = self.generator.create_view(handler, method, request=self.view.request)
                if hasattr(view, get_action(path, method, view)):
                    schemas[resource] = view.schema.get_request_body_schema(path, method)

        list_schemas = []
        for schema in schemas.values():
            if schema not in list_schemas:
                list_schemas.append(schema)
        if len(list_schemas) == 1:
            return list_schemas[0]
        return {'oneOf': list_schemas}

    def get_resources_response_schema(
        self, path: str, method: str, api_format: str = None
    ) -> OpenAPISchema:
        schemas = {}
        if self.generator:
            for resource, handler in self.get_resources(method).items():
                view = self.generator.create_view(handler, method, request=self.view.request)
                if hasattr(view, get_action(path, method, view)):
                    schemas[resource] = view.schema.get_response_schema(
                        path, method, api_format=api_format
                    )

        list_schemas = []
        for schema in schemas.values():
            if schema not in list_schemas:
                list_schemas.append(schema)
        if len(list_schemas) == 1:
            return list_schemas[0]
        return {'oneOf': list_schemas}

    def get_content_schema_by_type(self, path: str, method: str, schema_type: str) -> OpenAPISchema:
        content_schema = {}

        if schema_type == 'responses':
            resources_schema_method_name = 'get_resources_response_schema'
            schema_method_name = 'get_response_schema'
        else:
            resources_schema_method_name = 'get_resources_request_body_schema'
            schema_method_name = 'get_request_body_schema'

        vendor = getattr(settings, 'API_VENDOR_STRING', 'vendor').lower()
        default_content_type = f'application/vnd.{vendor}'

        resources_schema_method = getattr(self, resources_schema_method_name)
        content_schema[default_content_type] = {'schema': resources_schema_method(path, method)}

        if not self.generator:
            return content_schema

        version_content_type = f'{default_content_type}.{self.generator.api_version}'

        for resource, handler in self.view.resource_handlers_map.items():
            view = self.generator.create_view(handler, method, request=self.view.request)
            if not hasattr(view, get_action(path, method, view)):
                continue
            schema_method = getattr(view.schema, schema_method_name)
            default_resource_schema = schema_method(path, method)

            resource_content_type = f'{version_content_type}-{resource}'

            content_schema[resource_content_type] = {'schema': default_resource_schema}

            for api_format in self.generator.api_formats:
                if api_format != self.generator.api_default_format:
                    resource_schema = schema_method(path, method, api_format=api_format)
                    if resource_schema != default_resource_schema:
                        content_type = f'{resource_content_type}.{api_format}'
                        content_schema[content_type] = {'schema': resource_schema}

        return content_schema

    def get_request_body(self, path: str, method: str) -> OpenAPISchema:
        if method not in ('PUT', 'PATCH', 'POST'):
            return {}

        return {'content': self.get_content_schema_by_type(path, method, 'request_body')}

    def get_pagination_parameters(self, path: str, method: str) -> typing.List[OpenAPISchema]:
        handler = get_single_or_default_handler(self.view)

        if self.generator and handler:
            view = self.generator.create_view(handler, method, request=self.view.request)
            return view.schema.get_pagination_parameters(path, method)

        return []

    def get_filter_parameters(self, path: str, method: str) -> typing.List[OpenAPISchema]:
        handler = get_single_or_default_handler(self.view)

        if self.generator and handler:
            view = self.generator.create_view(handler, method, request=self.view.request)
            return view.schema.get_filter_parameters(path, method)

        return []

    def get_request_serializer_filter_parameters(
        self, path: str, method: str
    ) -> typing.List[OpenAPISchema]:
        handler = get_single_or_default_handler(self.view)

        if self.generator and handler:
            view = self.generator.create_view(handler, method, request=self.view.request)
            return view.schema.get_request_serializer_filter_parameters(path, method)

        return []

    def _get_resources(self, method: str) -> ResourceHandlersMap:
        return self.get_resources(method)

    def __get_item_schema(
        self, path: str, method: str, api_format: str = None
    ) -> typing.Optional[OpenAPISchema]:
        schemas = {}
        if self.generator:
            for resource, handler in self._get_resources(method).items():
                view = self.generator.create_view(handler, method, request=self.view.request)
                schemas[resource] = view.schema._get_item_schema(
                    path, method, api_format=api_format
                )

        list_schemas = list(schemas.values())
        if len(list_schemas) == 1:
            return list_schemas[0]
        return {'oneOf': list_schemas}

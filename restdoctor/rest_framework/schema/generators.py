from __future__ import annotations

import typing
from urllib.parse import urljoin

from django.conf import settings
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.schemas.openapi import SchemaGenerator

from restdoctor.rest_framework.schema.openapi import RestDoctorSchema
from restdoctor.rest_framework.schema.refs_registry import LocalRefsRegistry

if typing.TYPE_CHECKING:
    from restdoctor.rest_framework.custom_types import Handler
    from restdoctor.rest_framework.schema.custom_types import OpenAPISchema


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

    def create_view(
        self, callback: Handler, method: str, request: Request = None
    ) -> GenericAPIView:
        view = super().create_view(callback, method, request)
        schema_class = getattr(view, 'schema_class', RestDoctorSchema)
        view.schema = schema_class(generator=self)
        return view

    def get_error_schema(
        self, description: str = 'Описание ошибки', detailed: bool = False
    ) -> OpenAPISchema:
        schema: OpenAPISchema = {
            'type': 'object',
            'properties': {'message': {'type': 'string', 'description': description}},
        }
        if detailed:
            schema['properties']['errors'] = {'type': 'array', 'items': {'type': 'object'}}
        return schema

    def get_schema(
        self, request: Request = None, public: bool = False
    ) -> typing.Optional[OpenAPISchema]:
        self._initialise_endpoints()
        self.local_refs_registry.put_local_ref(
            '#/components/schemas/ErrorResponseSchemaDetailed', self.get_error_schema(detailed=True)
        )
        self.local_refs_registry.put_local_ref(
            '#/components/schemas/ErrorResponseSchema', self.get_error_schema()
        )
        self.local_refs_registry.put_local_ref(
            '#/components/schemas/NotFoundResponseSchema',
            self.get_error_schema(description='Ресурс не найден.'),
        )

        paths = self.get_paths(None if public else request)
        if not paths:
            return None

        schema = {'openapi': '3.0.2', 'info': self.get_info(), 'paths': paths}
        components = self.local_refs_registry.get_components()
        if components:
            schema['components'] = components

        return schema

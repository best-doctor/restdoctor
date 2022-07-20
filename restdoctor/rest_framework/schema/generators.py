from __future__ import annotations

import typing
from urllib.parse import urljoin

from django.conf import settings
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from semver import VersionInfo

from restdoctor.rest_framework.schema.custom_types import SchemaGenerator
from restdoctor.rest_framework.schema.openapi import RestDoctorSchema
from restdoctor.rest_framework.schema.refs_registry import LocalRefsRegistry
from restdoctor.utils.api_format import get_available_format
from restdoctor.utils.media_type import parse_accept

if typing.TYPE_CHECKING:
    from restdoctor.rest_framework.custom_types import Handler
    from restdoctor.rest_framework.schema.custom_types import OpenAPISchema


class RefsSchemaGenerator(SchemaGenerator):
    openapi_version = None

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        self.local_refs_registry = LocalRefsRegistry()

        if not self.openapi_version:
            self.openapi_version = VersionInfo.parse(settings.API_DEFAULT_OPENAPI_VERSION)

        self._operation_ids: typing.Dict[str, typing.Tuple[str, str]] = {}

        self.api_default_version = settings.API_DEFAULT_VERSION
        self.api_default_format = settings.API_DEFAULT_FORMAT
        self.api_default_content_type = f'application/vnd.{settings.API_VENDOR_STRING.lower()}'

        accept = kwargs.pop('accept', None)
        if accept:
            api_params = parse_accept(accept, settings.API_VENDOR_STRING.lower())

            api_version = api_params.version
            urlconf = settings.API_VERSIONS.get(api_version)
            if urlconf is None:
                raise Exception(f'Can not determine URLCONF for Accept string {accept}')
            self.api_version = api_version
            self.api_resource = api_params.resource_discriminator
            self.api_formats = [api_params.format]
            self.include_default_schema = False
        else:
            self.api_version = self.api_default_version
            urlconf = kwargs.pop('urlconf', None)
            if urlconf:
                for api_version, api_urlconf in settings.API_VERSIONS.items():
                    if api_urlconf == urlconf:
                        self.api_version = api_version
                        break

            self.api_resource = None
            self.api_formats = get_available_format(settings.API_FORMATS)
            self.include_default_schema = True

        kwargs['urlconf'] = urlconf
        super().__init__(*args, **kwargs)

    def get_paths(self, request: Request = None) -> typing.Optional[OpenAPISchema]:
        result: OpenAPISchema = {}

        paths, view_endpoints = self._get_paths_and_endpoints(request)

        if not paths:
            return None

        for path, method, view in view_endpoints:
            if not self.has_view_permissions(path, method, view):
                continue
            operation = view.schema.get_operation(path, method)

            operation_id = operation['operationId']
            if (
                operation_id in self._operation_ids
                and (method, path) != self._operation_ids[operation_id]
            ):
                operation_str = f'{view.__class__.__name__} {method, path}'
                action_name = view.schema.get_action_name(path, method)
                raise Exception(
                    f'Operation ID {operation_id} for view {operation_str} duplicates '
                    f'existing id for {self._operation_ids[operation_id]}. Consider adding '
                    f"schema_operation_id_map = {{ '{action_name}': '<your_custom_operation_id>' }} "
                    'to view/viewset to resolve this issue'
                )

            self._operation_ids[operation_id] = method, path

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

        schema = {'openapi': str(self.openapi_version), 'info': self.get_info(), 'paths': paths}
        components = self.local_refs_registry.get_components()
        if components:
            schema['components'] = components

        return schema

    def get_effective_api_format(self, api_format: str | None = None) -> str | None:
        effective_api_format = api_format
        if (
            effective_api_format is None
            and len(self.api_formats) == 1
            and self.api_formats[0] != self.api_default_format
        ):
            effective_api_format = self.api_formats[0]
        return effective_api_format

    def should_include_api_version(
        self, resource: str | None = None, api_format: str | None = None
    ) -> bool:
        return (
            not (self.api_version == self.api_default_version)
            or resource is not None
            or api_format is not None
        )

    def get_content_type(self, resource: str | None = None, api_format: str | None = None) -> str:
        effective_resource = resource or self.api_resource
        effective_api_format = self.get_effective_api_format(api_format=api_format)
        include_api_version = self.should_include_api_version(
            resource=effective_resource, api_format=effective_api_format
        )

        if effective_resource:
            content_type = (
                f'{self.api_default_content_type}.{self.api_version}-{effective_resource}'
            )
        elif include_api_version:
            content_type = f'{self.api_default_content_type}.{self.api_version}'
        else:
            content_type = f'{self.api_default_content_type}'

        if effective_api_format:
            content_type = f'{content_type}.{effective_api_format}'

        return content_type


class RefsSchemaGenerator30(RefsSchemaGenerator):
    openapi_version = VersionInfo.parse('3.0.2')


class RefsSchemaGenerator31(RefsSchemaGenerator):
    openapi_version = VersionInfo.parse('3.1.0')

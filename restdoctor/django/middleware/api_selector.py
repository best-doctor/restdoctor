from __future__ import annotations

import typing

from django.conf import settings

from restdoctor.utils.api_prefix import get_api_prefixes
from restdoctor.utils.media_type import get_api_header, parse_accept_header

if typing.TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

    from restdoctor.django.custom_types import DjangoHandler


class ApiSelectorMiddleware:
    def __init__(self, get_response: DjangoHandler):
        self.api_versions = settings.API_VERSIONS
        self.api_fallback_version = settings.API_FALLBACK_VERSION
        self.fallback_urlconf = self.api_versions.get(
            self.api_fallback_version, settings.ROOT_URLCONF
        )

        self.api_vendor_string = getattr(settings, 'API_VENDOR_STRING', 'Vendor')
        self.api_vendor_accept = self.api_vendor_string.lower()

        self.get_response = get_response
        self.api_prefixes = get_api_prefixes(default=None)
        self.schema_prefixes = tuple(
            f'{api_prefix}/openapi.schema' for api_prefix in (self.api_prefixes or [])
        )

    def is_api_call(self, request: HttpRequest) -> bool:
        if self.api_prefixes:
            return request.path_info.startswith(self.api_prefixes)

    def is_schema_call(self, request: HttpRequest) -> bool:
        return request.path_info.startswith(self.schema_prefixes)

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if not self.is_api_call(request):
            return self.get_response(request)

        if self.is_schema_call(request):
            api_params = parse_accept_header(
                f'application/vnd.{self.api_vendor_accept}', vendor=self.api_vendor_accept
            )
        else:
            api_params = parse_accept_header(
                request.headers.get('accept'), vendor=self.api_vendor_accept
            )
        request.api_params = api_params
        api_version = (api_params and api_params.version) or self.api_fallback_version
        request.urlconf = self.api_versions.get(api_version, self.fallback_urlconf)

        response = self.get_response(request)
        if api_params is not None:
            response[f'X-{self.api_vendor_string}-Media-Type'] = get_api_header(api_params)

        return response

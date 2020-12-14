from __future__ import annotations
import dataclasses
import typing

from django.conf import settings

from restdoctor.utils.api_prefix import get_api_prefix


@dataclasses.dataclass
class APIParams:
    accepted: str
    vendor: str
    prefix: typing.Optional[str] = None
    version: str = settings.API_FALLBACK_VERSION
    resource_discriminator: typing.Optional[str] = None
    format: str = settings.API_DEFAULT_FORMAT  # noqa: A003, VNE003

    @property
    def version_with_resource_discriminator(self) -> str:
        if self.resource_discriminator is None:
            return self.version
        else:
            return f'{self.version}-{self.resource_discriminator}'


def parse_accept(header: str = None, vendor: str = None) -> typing.Optional[APIParams]:
    if not header:
        return None
    api_params = APIParams(
        prefix=get_api_prefix(),
        accepted=header,
        vendor=vendor or 'vendor',
    )
    api_options_string = header.split('/', 1)[-1]
    if getattr(settings, 'API_FALLBACK_FOR_APPLICATION_JSON_ONLY', False):
        if api_options_string == 'json':
            return api_params
    elif not header.startswith(f'application/vnd.{api_params.vendor}'):
        return api_params

    api_params.version = settings.API_DEFAULT_VERSION

    api_options_string = api_options_string.split('+', 1)[0]

    parts = api_options_string.split('.')
    version = parse_version(parts)
    resource_discriminator = parse_resource_discriminator(parts)
    api_format = parse_api_format(parts)

    if version:
        api_params.version = version
    if resource_discriminator:
        api_params.resource_discriminator = resource_discriminator
    if api_format:
        api_params.format = api_format
    return api_params


def parse_version(api_options_parts: typing.List[str]) -> typing.Optional[str]:
    try:
        part = api_options_parts[2]
    except IndexError:
        pass
    else:
        version, *_ = part.split('-', 1)
        if version in settings.API_VERSIONS.keys():
            return version


def parse_resource_discriminator(api_options_parts: typing.List[str]) -> typing.Optional[str]:
    try:
        part = api_options_parts[2]
        return part.split('-', 1)[1]
    except IndexError:
        pass


def parse_api_format(api_options_parts: typing.List[str]) -> typing.Optional[str]:
    try:
        api_format = api_options_parts[3]
    except IndexError:
        pass
    else:
        if api_format in settings.API_FORMATS:
            return api_format


def get_api_header(params: APIParams) -> str:
    return f'{params.vendor}.{params.version_with_resource_discriminator}; format={params.format}'


def get_media_type(params: APIParams) -> str:
    if params.accepted.startswith('application/json'):
        return params.accepted

    return f'application/vnd.{params.vendor}.{params.version_with_resource_discriminator}.{params.format}+json'

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
    format: str = settings.API_DEFAULT_FORMAT  # noqa: A003, VNE003


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
    elif not header.startswith('application/vnd'):
        return api_params

    api_params.version = settings.API_DEFAULT_VERSION

    api_options_string = api_options_string.split('+', 1)[0]

    parts = api_options_string.split('.')
    for part in parts:
        if part in settings.API_VERSIONS.keys():
            api_params.version = part
        if part in settings.API_FORMATS:
            api_params.format = part
    return api_params


def get_api_header(params: APIParams) -> str:
    return f'bestdoctor.{params.version}; format={params.format}'


def get_media_type(params: APIParams) -> str:
    if params.accepted.startswith('application/json'):
        return params.accepted

    return f'application/vnd.{params.vendor}.{params.version}.{params.format}+json'

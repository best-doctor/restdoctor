from __future__ import annotations

import contextlib
import re
import typing

from django.conf import settings

from restdoctor.constants import DEFAULT_PREFIX_FORMAT_VERSION
from restdoctor.rest_framework.serializers import EmptySerializer

if typing.TYPE_CHECKING:
    from rest_framework.serializers import BaseSerializer

    from restdoctor.utils.custom_types import GenericContext

    SerializerType = typing.Type[BaseSerializer]
    SerializerClassMapItem = typing.Dict[str, SerializerType]
    SerializerClassMap = typing.Dict[str, typing.Union[SerializerType, SerializerClassMapItem]]


def get_from_serializer(
    serializer_class: BaseSerializer,
    data: GenericContext,
    instance: typing.Any = None,
    raise_exception: bool = True,
    **kwargs: typing.Any,
) -> GenericContext:
    serializer = get_serializer(serializer_class, instance, data, **kwargs)
    if serializer.is_valid(raise_exception=raise_exception):
        return serializer.validated_data
    return {}


def get_serializer(
    serializer_class: SerializerType,
    instance: typing.Any = None,
    data: typing.Optional[GenericContext] = None,
    **kwargs: typing.Any,
) -> BaseSerializer:
    return serializer_class(instance=instance, data=data, **kwargs)


def modify_instance(instance: typing.Any, update_data: GenericContext) -> bool:
    modified = False
    for key, value in update_data.items():
        old_value = getattr(instance, key)
        if old_value != value:
            setattr(instance, key, value)
            modified = True
    return modified


def update_instance(
    instance: typing.Any, update_data: GenericContext, save_if_modified: bool = True
) -> bool:
    modified = modify_instance(instance, update_data)
    if modified and save_if_modified:
        instance.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
    return modified


def get_serializer_class_from_map(
    action: str,
    stage: str,
    serializer_class_map: SerializerClassMap,
    default_class: SerializerType = EmptySerializer,
    use_default: bool = True,
    api_format: str = None,
) -> BaseSerializer:
    api_format = api_format or settings.API_DEFAULT_FORMAT
    if use_default:
        serializer_class = serializer_class_map.get('default', default_class)
        for format_name in get_api_formats(api_format):
            serializer_class = serializer_class_map.get(f'default.{format_name}', serializer_class)
    else:
        serializer_class = EmptySerializer

    action_class_map = serializer_class_map.get(action)
    if isinstance(action_class_map, dict):
        serializer_class = action_class_map.get(stage, serializer_class)
        for format_name in get_api_formats(api_format):
            serializer_class = action_class_map.get(f'{stage}.{format_name}', serializer_class)

    return serializer_class


def get_api_formats(api_format: str) -> typing.List[str]:
    result = [api_format]
    if DEFAULT_PREFIX_FORMAT_VERSION in api_format:
        api_format_name, api_format_version = api_format.split(DEFAULT_PREFIX_FORMAT_VERSION)
        for name in settings.API_FORMATS:
            if not all((name.startswith(api_format_name), DEFAULT_PREFIX_FORMAT_VERSION in name)):
                continue
            versions = re.search(r'\{(.+)\}', name)
            if not versions:
                continue
            with contextlib.suppress(IndexError, ValueError):
                versions_pool = sorted(versions.group(1).split(','), key=int)
                if not versions_pool:
                    break
                return [
                    f'{api_format_name}{DEFAULT_PREFIX_FORMAT_VERSION}{version}'
                    for version in versions_pool
                    if int(version) <= int(api_format_version)
                ]
    return result

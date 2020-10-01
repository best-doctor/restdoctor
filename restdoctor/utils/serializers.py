from __future__ import annotations
import typing

from django.conf import settings

if typing.TYPE_CHECKING:
    from rest_framework.serializers import BaseSerializer
    from utils.common_types import GenericContext

    SerializerClassMap = typing.Dict[str, typing.Any]
    SerializerType = typing.Type[BaseSerializer]


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


def modify_instance(
    instance: typing.Any,
    update_data: GenericContext,
) -> bool:
    modified = False
    for key, value in update_data.items():
        old_value = getattr(instance, key)
        if old_value != value:
            setattr(instance, key, value)
            modified = True
    return modified


def update_instance(
    instance: typing.Any,
    update_data: GenericContext,
    save_if_modified: bool = True,
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
    default_class: SerializerType,
    api_format: str = None,
) -> BaseSerializer:
    api_format = api_format or settings.API_DEFAULT_FORMAT
    serializer_class = serializer_class_map.get('default', default_class)
    serializer_class = serializer_class_map.get(f'default.{api_format}', serializer_class)

    action_class_map = serializer_class_map.get(action)
    if isinstance(action_class_map, dict):
        serializer_class = action_class_map.get(stage, serializer_class)
        serializer_class = action_class_map.get(f'{stage}.{api_format}', serializer_class)
    return serializer_class

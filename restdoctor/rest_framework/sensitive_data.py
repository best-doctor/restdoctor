from __future__ import annotations

import contextlib
import copy
import inspect
import typing

from django.db.models import Model
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import Serializer, ListSerializer

from restdoctor.django.sensitive_data import get_model_sensitive_fields, is_model_field_sensitive

if typing.TYPE_CHECKING:
    SerializerClassOrInstance = typing.Union[typing.Type[Serializer], Serializer]
    SensitiveDataConfig = typing.Dict[str, typing.Any]
    SensitiveDataConfigValue = typing.Union[bool, SensitiveDataConfig]
    SerializerData = typing.Union[typing.Dict[str, typing.Any], typing.List[typing.Dict[str, typing.Any]]]


def get_serializer_sensitive_fields(
    serializer: Serializer, with_model_sensitive_fields: bool = True,
) -> typing.List[str]:
    sensitive_fields = []

    with contextlib.suppress(AttributeError, TypeError):
        sensitive_fields.extend(serializer.SensitiveData.include)

    if with_model_sensitive_fields:
        with contextlib.suppress(AttributeError, TypeError):
            sensitive_fields.extend(get_model_sensitive_fields(serializer.Meta.model))

    return sensitive_fields


def get_serializer_instance(serializer: SerializerClassOrInstance) -> Serializer:
    return serializer() if inspect.isclass(serializer) else serializer


def get_field_serializer(
    serializer: Serializer, field_name: str, field: typing.Any,
) -> typing.Optional[Serializer]:
    if isinstance(field, Serializer):
        return field
    elif isinstance(field, ListSerializer):
        return field.child
    elif isinstance(field, SerializerMethodField):
        if (
            field_name in serializer.__class__._declared_fields
            and hasattr(serializer.__class__._declared_fields[field_name], 'schema_type')
            and isinstance(serializer.__class__._declared_fields[field_name].schema_type, Serializer)
        ):
            return serializer.__class__._declared_fields[field_name].schema_type


def get_serializer_sensitive_data_config(
    serializer: SerializerClassOrInstance,
) -> SensitiveDataConfig:
    sensitive_data_config: SensitiveDataConfig = {}

    serializer = get_serializer_instance(serializer)

    try:
        model = serializer.Meta.model
    except AttributeError:
        model = None

    for field_name, field in serializer.get_fields().items():
        result = get_field_sensitive_data_config(
            field_name, field, serializer, model,
        )
        if result:
            sensitive_data_config[field_name] = result

    return sensitive_data_config


def get_field_sensitive_data_config(
    field_name: str,
    field: typing.Any,
    serializer: Serializer,
    model: typing.Optional[Model],
) -> SensitiveDataConfigValue:
    result: SensitiveDataConfigValue = False

    field_serializer = get_field_serializer(serializer, field_name, field)
    field_source = getattr(field, 'source', None)

    if field_name in get_serializer_sensitive_fields(serializer):
        result = True
    elif field_serializer is not None:
        result = get_serializer_sensitive_data_config(field_serializer)
    elif field_source is not None and field_source != '*' and model:
        result = is_model_field_sensitive(model, field.source)

    return result


def clear_sensitive_data(
    data: SerializerData,
    serializer: SerializerClassOrInstance,
) -> SerializerData:
    data = copy.deepcopy(data)

    try:
        sensitive_data_config = get_serializer_sensitive_data_config(serializer)
    except AttributeError:
        return data

    if not sensitive_data_config:
        return data

    for field_name, field_value in sensitive_data_config.items():
        clear_sensitive_field(field_name, field_value, data)

    return data


def clear_sensitive_field(
    field_name: str, field_value: typing.Any, data: SerializerData,
) -> None:
    if isinstance(data, list):
        for data_item in data:
            clear_sensitive_field(field_name, field_value, data_item)
    elif isinstance(data, dict) and field_name in data:
        if isinstance(field_value, dict):
            for related_field_name, related_field_value in field_value.items():
                clear_sensitive_field(related_field_name, related_field_value, data[field_name])
        else:
            data[field_name] = '[Cleaned]'

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

if TYPE_CHECKING:
    from django.db.models import Model

from rest_framework.serializers import (
    ModelSerializer as BaseModelSerializer, Serializer as BaseSerializer,
    SerializerMetaclass as BaseSerializerMetaclass,
)


def _is_serializer_subclass(obj: Any) -> bool:
    try:
        return issubclass(obj, Serializer)
    except TypeError:
        return False


def _get_serializer_fields(serializer_cls: Serializer) -> List[str]:
    try:
        return list(serializer_cls.Meta.fields)
    except AttributeError:
        return list(serializer_cls._declared_fields)


class _DeferredMetaFields(tuple):
    pass


def extend_meta_fields(*args: Union[Serializer, str]) -> _DeferredMetaFields:
    return _DeferredMetaFields(args)


class SerializerMetaclass(BaseSerializerMetaclass):
    def __new__(cls, name: str, bases: Tuple, attrs: Dict[str, Any]) -> SerializerMetaclass:
        meta = attrs.get('Meta')
        if meta:
            fields = getattr(meta, 'fields', None)
            if isinstance(fields, _DeferredMetaFields):
                meta.fields = cls._extend_meta_fields(fields, bases)
        return super().__new__(cls, name, bases, attrs)

    @classmethod
    def _extend_meta_fields(cls, deferred_fields: _DeferredMetaFields, bases: Tuple) -> List[str]:
        fields: List[str] = []
        serializer_in_fields = False
        for arg in deferred_fields:
            if isinstance(arg, str):
                fields.append(arg)
            elif _is_serializer_subclass(arg):
                fields.extend(_get_serializer_fields(arg))
                serializer_in_fields = True
            else:
                raise TypeError(f'str or Serializer subclass expected, got {arg!r}')
        if serializer_in_fields:
            return fields
        parent_fields: List[str] = []
        for parent_cls in bases:
            parent_fields.extend(_get_serializer_fields(parent_cls))
        return parent_fields + fields


class ModelSerializerMetaclass(SerializerMetaclass):
    def __new__(cls, name: str, bases: Tuple, attrs: Dict[str, Any]) -> ModelSerializerMetaclass:
        serializer_cls = super().__new__(cls, name, bases, attrs)
        meta = attrs.get('Meta')
        if meta:
            if not hasattr(meta, 'model'):
                model = cls._get_meta_model(serializer_cls)
                if model:
                    meta.model = model
            fields = getattr(meta, 'fields', None)
            if isinstance(fields, _DeferredMetaFields):
                meta.fields = cls._extend_meta_fields(fields, bases)
        return serializer_cls

    @classmethod
    def _get_meta_model(cls, serializer_cls: ModelSerializer) -> Optional[Model]:
        for parent_cls in inspect.getmro(serializer_cls):
            parent_meta = parent_cls.__dict__.get('Meta')
            if parent_meta and hasattr(parent_meta, 'model'):
                return parent_meta.model
        return None


class Serializer(BaseSerializer, metaclass=SerializerMetaclass):
    pass


class EmptySerializer(Serializer):
    pass


class ModelSerializer(BaseModelSerializer, Serializer, metaclass=ModelSerializerMetaclass):
    pass

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type, Union

if TYPE_CHECKING:
    from django.db.models import Model

from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import BaseSerializer as BaseDRFSerializer
from rest_framework.serializers import ModelSerializer as BaseModelSerializer
from rest_framework.serializers import Serializer as BaseSerializer
from rest_framework.serializers import SerializerMetaclass as BaseSerializerMetaclass

from restdoctor.utils.pydantic import convert_pydantic_errors_to_drf_errors


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


class PydanticModelSerializer(BaseDRFSerializer):
    """Serializer for pydantic models."""

    pydantic_model: Type[BaseModel]

    def __new__(cls, *args: list[Any], **kwargs: dict[str, Any]):  # type: ignore
        pydantic_model = getattr(cls, 'pydantic_model', None)
        if not inspect.isclass(pydantic_model) or not issubclass(pydantic_model, BaseModel):
            raise AttributeError(
                'Class attribute "pydantic_model" is mandatory for this serializer'
            )
        return super().__new__(cls, *args, **kwargs)

    def to_internal_value(self, data: dict[str, Any]) -> BaseModel:
        try:
            pydantic_model = self.pydantic_model(**data)
        except PydanticValidationError as exc:
            errors = convert_pydantic_errors_to_drf_errors(exc.errors())
            raise ValidationError(errors)
        return pydantic_model

    def to_representation(
        self, instance: PydanticModelSerializer | BaseModel | dict
    ) -> dict[str, Any]:
        if isinstance(instance, dict):
            value = self.to_internal_value(instance).dict()
        elif isinstance(instance, BaseModel):
            value = instance.dict()
        elif isinstance(instance, PydanticModelSerializer):
            instance.is_valid()
            value = instance._pydantic_instance.dict()
        else:
            raise TypeError('Unknown type of instance for representation')
        return value

    def is_valid(self, raise_exception: bool = False) -> bool:
        if not hasattr(self, 'initial_data'):
            raise AssertionError(
                'Cannot call `.is_valid()` as no `data=` keyword argument was '
                'passed when instantiating the serializer instance.'
            )
        if not hasattr(self, '_validated_data'):
            try:
                pydantic_instance = self.pydantic_model(**self.initial_data)
                self._pydantic_instance = pydantic_instance
                self._validated_data = pydantic_instance.dict()
            except PydanticValidationError as exc:
                self._validated_data = {}
                self._errors = convert_pydantic_errors_to_drf_errors(exc.errors())
            else:
                self._errors = {}

        if self._errors and raise_exception:
            raise ValidationError(self.errors)

        return not bool(self._errors)

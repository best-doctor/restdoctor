from __future__ import annotations

import inspect
import typing

if typing.TYPE_CHECKING:
    from restdoctor.rest_framework.custom_types import ModelObject, GenericRepresentation

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model as DjangoModel
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from rest_framework.exceptions import ValidationError
from rest_framework.fields import empty
from rest_framework.serializers import BaseSerializer as BaseDRFSerializer
from rest_framework.serializers import ModelSerializer as BaseModelSerializer
from rest_framework.serializers import Serializer as BaseSerializer
from rest_framework.serializers import SerializerMetaclass as BaseSerializerMetaclass
from rest_framework.utils import model_meta

from restdoctor.utils.pydantic import convert_pydantic_errors_to_drf_errors


def _is_serializer_subclass(obj: typing.Any) -> bool:
    try:
        return issubclass(obj, Serializer)
    except TypeError:
        return False


def _get_serializer_fields(serializer_cls: Serializer) -> list[str]:
    try:
        return list(serializer_cls.Meta.fields)
    except AttributeError:
        return list(serializer_cls._declared_fields)


class _DeferredMetaFields(tuple):
    pass


def extend_meta_fields(*args: Serializer | str | None) -> _DeferredMetaFields:
    return _DeferredMetaFields(args)


class SerializerMetaclass(BaseSerializerMetaclass):
    def __new__(cls, name: str, bases: tuple, attrs: dict[str, typing.Any]) -> SerializerMetaclass:
        meta = attrs.get('Meta')
        if meta:
            fields = getattr(meta, 'fields', None)
            if isinstance(fields, _DeferredMetaFields):
                meta.fields = cls._extend_meta_fields(fields, bases)
        return super().__new__(cls, name, bases, attrs)

    @classmethod
    def _extend_meta_fields(cls, deferred_fields: _DeferredMetaFields, bases: tuple) -> list[str]:
        fields: list[str] = []
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
        parent_fields: list[str] = []
        for parent_cls in bases:
            parent_fields.extend(_get_serializer_fields(parent_cls))
        return parent_fields + fields


class ModelSerializerMetaclass(SerializerMetaclass):
    def __new__(
        cls, name: str, bases: tuple, attrs: dict[str, typing.Any]
    ) -> ModelSerializerMetaclass:
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
    def _get_meta_model(cls, serializer_cls: ModelSerializer) -> typing.Optional[ModelObject]:
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


class PydanticSerializer(BaseDRFSerializer):
    """Serializer for pydantic models."""

    class Meta:
        model: typing.Optional[typing.Type[DjangoModel]] = None

    pydantic_model: typing.Type[BaseModel]

    def __new__(cls, *args: list[typing.Any], **kwargs: dict[str, typing.Any]):  # type: ignore
        if not hasattr(cls, 'pydantic_model'):
            raise AttributeError(
                'Class attribute "pydantic_model" is mandatory for this serializer'
            )
        if not inspect.isclass(cls.pydantic_model) or not issubclass(cls.pydantic_model, BaseModel):
            raise AttributeError(
                'Class attribute "pydantic_model" must be an instance of pydantic.BaseModel'
            )
        cls._validate_django_model()
        return super().__new__(cls, *args, **kwargs)

    def __init__(
        self,
        instance: ModelObject | None = None,
        data: dict[str, typing.Any] | empty = empty,
        **kwargs: dict[str, typing.Any],
    ):
        self._pydantic_instance: BaseModel | None = None
        self._setup_create_update_methods()
        super().__init__(instance=instance, data=data, **kwargs)

    @classmethod
    def _validate_django_model(cls) -> None:
        model = getattr(cls.Meta, 'model', None)
        if not model:
            return
        cls._validate_django_model_fields(model)
        cls._validate_meta_fields_not_exist()
        cls._validate_orm_mode_enabled()

    @classmethod
    def _validate_django_model_fields(cls, model: DjangoModel) -> None:
        pydantic_fields_set = set(cls.pydantic_model.__fields__.keys())
        model_info = model_meta.get_field_info(model)
        model_fields = list(model_info.fields.keys())
        model_fields.extend(model_info.relations.keys())
        if not pydantic_fields_set.issubset(model_fields):
            raise ImproperlyConfigured('Pydantic model fields is not subset of django model fields')

    @classmethod
    def _validate_meta_fields_not_exist(cls) -> None:
        meta_fields = getattr(cls.Meta, 'fields', None)
        if meta_fields is not None:
            raise ImproperlyConfigured(
                'Meta.fields does not affect this serializer behavior. Remove this attribute'
            )

    @classmethod
    def _validate_orm_mode_enabled(cls) -> None:
        if not getattr(cls.pydantic_model.Config, 'orm_mode', False):
            raise ImproperlyConfigured(
                'pydantic_model.Config.orm_mode must be True for this serializer'
            )

    def to_internal_value(self, data: dict[str, typing.Any]) -> BaseModel:
        try:
            pydantic_model = self.pydantic_model(**data)
        except PydanticValidationError as exc:
            errors = convert_pydantic_errors_to_drf_errors(exc.errors())
            raise ValidationError(errors)
        return pydantic_model

    def to_representation(  # noqa: CAC001
        self, instance: PydanticSerializer | BaseModel | DjangoModel | dict
    ) -> GenericRepresentation:
        # Типы аргумента instance были выяснены экспериментальным путем
        # в ходе тестирования
        if isinstance(instance, dict):
            value = self.to_internal_value(instance).dict()
        elif isinstance(instance, BaseModel):
            value = instance.dict()
        elif isinstance(instance, PydanticSerializer):
            instance.is_valid(raise_exception=True)
            value = instance._pydantic_instance.dict()  # type: ignore
        elif isinstance(instance, DjangoModel):
            value = self._django_model_to_representation(instance)
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

    def _django_model_to_representation(self, instance: DjangoModel) -> GenericRepresentation:
        try:
            value = self.pydantic_model.from_orm(instance).dict()
        except PydanticValidationError as exc:
            raise ValidationError(convert_pydantic_errors_to_drf_errors(exc.errors()))
        return value

    def _setup_create_update_methods(self) -> None:
        self._writable_fields = ()  # for disable unwanted validation in create and update methods
        self.create = BaseModelSerializer.create.__get__(self, self.__class__)
        self.update = BaseModelSerializer.update.__get__(self, self.__class__)

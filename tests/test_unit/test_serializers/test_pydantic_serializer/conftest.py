from __future__ import annotations

import datetime
import typing
from unittest.mock import Mock

import pytest
from django.db import models
from pydantic import BaseModel, Field, Json, StrictInt, StrictStr

from restdoctor.rest_framework.serializers import PydanticSerializer


class PydanticTestModel(BaseModel):
    class Config:
        orm_mode = True

    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    field_a: StrictStr
    field_b: StrictInt


class PydanticWithQueryParamsTestModel(BaseModel):
    any_int: int = Field(alias='my_int')
    any_str: str = Field(alias='any_str')
    any_json: Json
    any_list: list
    any_str_list: typing.List[str]
    any_bool: bool


class PydanticWithQueryParamsShortTestModel(BaseModel):
    any_int: int
    any_str: str


class PydanticObjectTestModel(BaseModel):
    class Config:
        allow_population_by_field_name = True

    object_id: int = Field(alias='id')


class PydanticTestModelWithAliases(PydanticTestModel):
    class Config:
        allow_population_by_field_name = True

    object_type: str = Field(alias='type')
    model_object: PydanticObjectTestModel = Field(alias='object')


class DjangoTestModel(models.Model):
    class Meta:
        app_label = 'fake_app'

    field_a = models.TextField()
    field_b = models.TextField()
    created_at = models.DateTimeField()


class TestPydanticSerializer(PydanticSerializer):
    class Meta:
        pydantic_model = PydanticTestModel


class TestPydanticQuerySerializer(PydanticSerializer):
    class Meta:
        pydantic_model = PydanticWithQueryParamsTestModel


class TestPydanticShortQuerySerializer(PydanticSerializer):
    class Meta:
        pydantic_model = PydanticWithQueryParamsShortTestModel


class TestPydanticSerializerWithAliases(PydanticSerializer):
    class Meta:
        pydantic_model = PydanticTestModelWithAliases
        pydantic_use_aliases = True


class TestPydanticSerializerDeprecated(PydanticSerializer):
    pydantic_model = PydanticTestModel


class TestPydanticSerializerWithAliasesDeprecated(PydanticSerializer):
    class Meta:
        pydantic_use_aliases = True

    pydantic_model = PydanticTestModelWithAliases


class TestPydanticDtoWithSensitiveData(BaseModel):
    first_name: str
    last_name: str
    title: str


class PydanticSerializerWithSensitiveData(PydanticSerializer):
    class Meta:
        pydantic_model = TestPydanticDtoWithSensitiveData

    class SensitiveData:
        include = ['first_name', 'last_name']


@pytest.fixture()
def pydantic_test_model() -> typing.Type[PydanticSerializer]:
    return PydanticTestModel


@pytest.fixture()
def pydantic_test_with_query_model() -> typing.Type[PydanticSerializer]:
    return PydanticWithQueryParamsTestModel


@pytest.fixture()
def pydantic_test_model_with_aliases() -> typing.Type[PydanticSerializer]:
    return PydanticTestModelWithAliases


@pytest.fixture()
def pydantic_model_test_serializer() -> typing.Type[PydanticSerializer]:
    return TestPydanticSerializer


@pytest.fixture()
def pydantic_test_query_serializer() -> typing.Type[PydanticSerializer]:
    return TestPydanticQuerySerializer


@pytest.fixture()
def pydantic_shot_test_query_serializer() -> typing.Type[PydanticSerializer]:
    return TestPydanticShortQuerySerializer


@pytest.fixture()
def pydantic_model_with_aliases_test_serializer() -> typing.Type[PydanticSerializer]:
    return TestPydanticSerializerWithAliases


@pytest.fixture()
def pydantic_model_test_serializer_deprecated() -> typing.Type[PydanticSerializer]:
    return TestPydanticSerializerDeprecated


@pytest.fixture()
def pydantic_model_with_aliases_test_serializer_deprecated() -> typing.Type[PydanticSerializer]:
    return TestPydanticSerializerWithAliasesDeprecated


@pytest.fixture()
def django_test_model(mocker) -> DjangoTestModel:
    mocker.patch.object(DjangoTestModel._meta, 'default_manager')
    mocker.patch.object(DjangoTestModel, 'save')
    return DjangoTestModel


@pytest.fixture()
def pydantic_django_model_test_serializer(
    pydantic_test_model: BaseModel, django_test_model: models.Model
) -> typing.Type[PydanticSerializer]:
    class TestPydanticDjangoModelSerializer(PydanticSerializer):
        class Meta:
            model = django_test_model
            pydantic_model = pydantic_test_model

    return TestPydanticDjangoModelSerializer


@pytest.fixture()
def pydantic_django_model_test_serializer_deprecated(
    pydantic_test_model: BaseModel, django_test_model: models.Model
) -> typing.Type[PydanticSerializer]:
    class TestPydanticDjangoModelSerializer(PydanticSerializer):
        class Meta:
            model = django_test_model

        pydantic_model = pydantic_test_model

    return TestPydanticDjangoModelSerializer


@pytest.fixture()
def pydantic_test_model_data() -> dict[str, str | int]:
    return {
        'created_at': datetime.datetime.utcnow().timestamp(),
        'field_a': 'Test text',
        'field_b': 1,
    }


@pytest.fixture()
def pydantic_test_query_data() -> dict:
    return {
        'my_int': 10,
        'any_str': 'hi',
        'any_json': '{"foo": "bar"}',
        'any_list': ['1', '2'],
        'any_bool': True,
        'any_str_list': ['one'],
    }


@pytest.fixture()
def pydantic_test_model_with_aliases_data(pydantic_test_model_data) -> dict[str, str | int]:
    return {**pydantic_test_model_data, 'type': 'test', 'object': {'id': 1}}


@pytest.fixture()
def serialized_pydantic_test_model_data(
    pydantic_test_model_data, pydantic_test_model
) -> dict[str, str | datetime.datetime]:
    return pydantic_test_model(**pydantic_test_model_data).dict()


@pytest.fixture()
def serialized_pydantic_test_with_query(
    pydantic_test_query_data, pydantic_test_with_query_model
) -> dict[str, str | datetime.datetime]:
    return pydantic_test_with_query_model(**pydantic_test_query_data).dict()


@pytest.fixture()
def serialized_pydantic_test_model_with_aliases_data(
    pydantic_test_model_with_aliases_data, pydantic_test_model_with_aliases
) -> dict[str, str | datetime.datetime]:
    return pydantic_test_model_with_aliases(**pydantic_test_model_with_aliases_data).dict(
        by_alias=True
    )


@pytest.fixture()
def pydantic_model_serializer_with_sensitive_data() -> typing.Type[
    PydanticSerializerWithSensitiveData
]:
    return PydanticSerializerWithSensitiveData


@pytest.fixture()
def mocked__query_dict_to_dict(mock_for_module) -> Mock:
    return mock_for_module(
        module_name='restdoctor.rest_framework.serializers.PydanticSerializer',
        function_name='query_dict_to_dict',
    )


@pytest.fixture()
def mocked__is_sequence_field(mock_for_module) -> Mock:
    return mock_for_module(
        module_name='restdoctor.rest_framework.serializers.PydanticSerializer',
        function_name='_is_sequence_field',
    )

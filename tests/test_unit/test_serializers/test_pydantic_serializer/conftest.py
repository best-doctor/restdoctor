from __future__ import annotations

import datetime

import pytest
from django.db import models
from pydantic import BaseModel, Field, StrictInt, StrictStr

from restdoctor.rest_framework.serializers import PydanticSerializer


class PydanticTestModel(BaseModel):
    class Config:
        orm_mode = True

    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    field_a: StrictStr
    field_b: StrictInt


class DjangoTestModel(models.Model):
    class Meta:
        app_label = 'fake_app'

    field_a = models.TextField()
    field_b = models.TextField()
    created_at = models.DateTimeField()


class TestPydanticSerializer(PydanticSerializer):
    pydantic_model = PydanticTestModel


@pytest.fixture()
def pydantic_test_model() -> PydanticTestModel:
    return PydanticTestModel


@pytest.fixture()
def pydantic_model_test_serializer() -> TestPydanticSerializer:
    return TestPydanticSerializer


@pytest.fixture()
def django_test_model(mocker) -> DjangoTestModel:
    mocker.patch.object(DjangoTestModel._meta, 'default_manager')
    mocker.patch.object(DjangoTestModel, 'save')
    return DjangoTestModel


@pytest.fixture()
def pydantic_django_model_test_serializer(
    pydantic_test_model: BaseModel, django_test_model: models.Model
) -> PydanticSerializer:
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
def serialized_pydantic_test_model_data(
    pydantic_test_model_data, pydantic_test_model
) -> dict[str, str | datetime.datetime]:
    return pydantic_test_model(**pydantic_test_model_data).dict()

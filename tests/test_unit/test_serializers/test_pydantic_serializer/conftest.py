from __future__ import annotations

import datetime

import pytest
from pydantic import BaseModel, Field, StrictInt, StrictStr

from restdoctor.rest_framework.serializers import PydanticSerializer


class PydanticTestModel(BaseModel):
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    field_a: StrictStr
    field_b: StrictInt


class TestPydanticSerializer(PydanticSerializer):
    pydantic_model = PydanticTestModel


@pytest.fixture()
def pydantic_test_model() -> PydanticTestModel:
    return PydanticTestModel


@pytest.fixture()
def pydantic_model_test_serializer() -> TestPydanticSerializer:
    return TestPydanticSerializer


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

from __future__ import annotations

import datetime

import pytest
from pydantic import BaseModel, Field, StrictInt, StrictStr

from restdoctor.rest_framework.serializers import PydanticModelSerializer


class TestPydanticModel(BaseModel):
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    field_a: StrictStr
    field_b: StrictInt


class TestPydanticModelSerializer(PydanticModelSerializer):
    pydantic_model = TestPydanticModel


@pytest.fixture()
def pydantic_test_model() -> TestPydanticModel:
    return TestPydanticModel


@pytest.fixture()
def pydantic_model_test_serializer() -> TestPydanticModelSerializer:
    return TestPydanticModelSerializer


@pytest.fixture()
def pydantic_test_model_data() -> dict[str, str | int]:
    return {
        'created_at': datetime.datetime.utcnow().timestamp(),
        'field_a': 'Test text',
        'field_b': 1,
    }

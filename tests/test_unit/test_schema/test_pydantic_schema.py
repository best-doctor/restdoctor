from __future__ import annotations

import datetime

import pytest
from pydantic import BaseModel, Field, StrictInt, StrictStr

from restdoctor.rest_framework.schema.openapi import RestDoctorSchema
from restdoctor.rest_framework.serializers import PydanticSerializer


class PydanticTestModel(BaseModel):
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    field_a: StrictStr
    field_b: StrictInt


class TestPydanticSerializer(PydanticSerializer):
    pydantic_model = PydanticTestModel


@pytest.fixture()
def expected_schema():
    return {
        'title': 'PydanticTestModel',
        'type': 'object',
        'properties': {
            'created_at': {'title': 'Created At', 'type': 'string', 'format': 'date-time'},
            'field_a': {'title': 'Field A', 'type': 'string'},
            'field_b': {'title': 'Field B', 'type': 'integer'},
        },
        'required': ['field_a', 'field_b'],
    }


def test_get_response_schema_success_case(expected_schema):
    assert RestDoctorSchema().get_serializer_schema(TestPydanticSerializer()) == expected_schema

from __future__ import annotations

import copy
import datetime

import pytest
from pydantic import BaseModel, Field, StrictInt, StrictStr

from restdoctor.rest_framework.schema.generators import RefsSchemaGenerator
from restdoctor.rest_framework.schema.openapi import RestDoctorSchema
from restdoctor.rest_framework.schema.serializers import OPENAPI_REF_PREFIX
from restdoctor.rest_framework.serializers import PydanticSerializer


class PydanticTestModel(BaseModel):
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    field_a: StrictStr
    field_b: StrictInt


class PydanticNestedTestModel(BaseModel):
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    nested_field: PydanticTestModel


class PydanticTestSerializer(PydanticSerializer):
    pydantic_model = PydanticTestModel


class NestedPydanticTestSerializer(PydanticSerializer):
    pydantic_model = PydanticNestedTestModel


@pytest.fixture()
def test_model_schema():
    return {
        'description': 'PydanticTestModel',
        'type': 'object',
        'properties': {
            'created_at': {'description': 'Created At', 'type': 'string', 'format': 'date-time'},
            'field_a': {'description': 'Field A', 'type': 'string'},
            'field_b': {'description': 'Field B', 'type': 'integer'},
        },
        'required': ['field_a', 'field_b'],
    }


@pytest.fixture()
def test_nested_model_schema_without_definitions():
    return {
        'description': 'PydanticNestedTestModel',
        'type': 'object',
        'properties': {
            'created_at': {'description': 'Created At', 'type': 'string', 'format': 'date-time'},
            'nested_field': {'$ref': f'{OPENAPI_REF_PREFIX}PydanticTestModel'},
        },
        'required': ['nested_field'],
    }


@pytest.fixture()
def test_nested_model_schema(test_model_schema, test_nested_model_schema_without_definitions):
    schema = copy.deepcopy(test_nested_model_schema_without_definitions)
    schema['properties']['nested_field'] = {'$ref': '#/definitions/PydanticTestModel'}
    schema['definitions'] = {'PydanticTestModel': test_model_schema}
    return schema


def test_get_serializer_schema_success_case(test_model_schema):
    schema = RestDoctorSchema().get_serializer_schema(PydanticTestSerializer())

    assert schema == test_model_schema


def test_map_serializer_without_generator_success_case(test_model_schema):
    schema = RestDoctorSchema().map_serializer(PydanticTestSerializer())

    assert schema == test_model_schema


def test_map_serializer_with_generator_success_case(test_model_schema):
    schema_generator = RefsSchemaGenerator()
    schema = RestDoctorSchema(generator=schema_generator).map_serializer(PydanticTestSerializer())
    ref = f'{OPENAPI_REF_PREFIX}PydanticTestModel'

    assert schema == {'$ref': ref}
    assert schema_generator.local_refs_registry.get_local_ref(ref) == test_model_schema


def test_get_serializer_schema_for_nested_serializer_success_case(test_nested_model_schema):
    schema = RestDoctorSchema().get_serializer_schema(NestedPydanticTestSerializer())

    assert schema == test_nested_model_schema


def test_map_serializer_with_nested_serializer_success_case(test_nested_model_schema):
    schema = RestDoctorSchema().map_serializer(NestedPydanticTestSerializer())

    assert schema == test_nested_model_schema


def test_map_serializer_with_refs_generator_with_nested_serializer_success_case(
    test_nested_model_schema_without_definitions, test_model_schema
):
    schema_generator = RefsSchemaGenerator()
    schema = RestDoctorSchema(generator=schema_generator).map_serializer(
        NestedPydanticTestSerializer()
    )
    ref = f'{OPENAPI_REF_PREFIX}PydanticNestedTestModel'
    nested_ref = test_nested_model_schema_without_definitions['properties']['nested_field']['$ref']

    assert schema == {'$ref': ref}
    assert (
        schema_generator.local_refs_registry.get_local_ref(ref)
        == test_nested_model_schema_without_definitions
    )
    assert schema_generator.local_refs_registry.get_local_ref(nested_ref) == test_model_schema

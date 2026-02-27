from __future__ import annotations

import copy
import datetime
import typing
from uuid import UUID

import pytest
from pydantic.v1 import BaseModel, Field, StrictInt, StrictStr

from restdoctor.rest_framework.schema.generators import RefsSchemaGenerator
from restdoctor.rest_framework.schema.openapi import RestDoctorSchema
from restdoctor.rest_framework.schema.serializers import OPENAPI_REF_PREFIX
from restdoctor.rest_framework.serializers import PydanticSerializer
from tests.test_unit.conftest import TestTextChoices


class PydanticTestModel(BaseModel):
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    field_a: StrictStr
    field_b: StrictInt
    title: str


class PydanticTestQueryModel(BaseModel):
    boolean_param: typing.Optional[bool] = Field(description='Boolean filter param')
    string_param: str
    integer_param: typing.Optional[int]
    uuid_list_param: typing.Optional[typing.List[UUID]]
    text_choices_param: TestTextChoices


class PydanticNestedTestModel(BaseModel):
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    nested_field: PydanticTestModel


class PydanticTestSerializer(PydanticSerializer):
    pydantic_model = PydanticTestModel


class NestedPydanticTestSerializer(PydanticSerializer):
    pydantic_model = PydanticNestedTestModel


class PydanticTestQuerySerializer(PydanticSerializer):
    class Meta:
        pydantic_model = PydanticTestQueryModel


@pytest.fixture()
def test_model_schema():
    return {
        'description': 'PydanticTestModel',
        'type': 'object',
        'properties': {
            'created_at': {'description': 'Created At', 'type': 'string', 'format': 'date-time'},
            'field_a': {'description': 'Field A', 'type': 'string'},
            'field_b': {'description': 'Field B', 'type': 'integer'},
            'title': {'description': 'Title', 'type': 'string'},
        },
        'required': ['field_a', 'field_b', 'title'],
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


def test__serializer_schema():
    serializer_schema = RestDoctorSchema().serializer_schema
    expected_data = [
        {
            'in': 'query',
            'name': 'boolean_param',
            'required': False,
            'schema': {'description': 'Boolean filter param', 'type': 'boolean'},
        },
        {
            'in': 'query',
            'name': 'string_param',
            'required': True,
            'schema': {'description': 'String Param', 'type': 'string'},
        },
        {
            'in': 'query',
            'name': 'integer_param',
            'required': False,
            'schema': {'description': 'Integer Param', 'type': 'integer'},
        },
        {
            'in': 'query',
            'name': 'uuid_list_param',
            'required': False,
            'schema': {
                'description': 'Uuid List Param',
                'items': {'format': 'uuid', 'type': 'string'},
                'type': 'array',
            },
        },
        {
            'in': 'query',
            'name': 'text_choices_param',
            'required': True,
            'schema': {'$ref': '#/components/schemas/TestTextChoices'},
        },
    ]

    result = serializer_schema.map_pydantic_query_serializer(PydanticTestQuerySerializer())

    assert result == expected_data

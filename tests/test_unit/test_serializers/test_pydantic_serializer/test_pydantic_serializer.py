from __future__ import annotations

import sys

from unittest.mock import call

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.http import QueryDict
from pydantic import BaseModel
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ListSerializer

from restdoctor.rest_framework.serializers import PydanticSerializer

if sys.version_info.major == 3 and sys.version_info.minor == 8:
    from tests.test_unit.test_serializers.test_pydantic_serializer.parameters_38 import PARAMETRIZE_TYPES
else:
    from tests.test_unit.test_serializers.test_pydantic_serializer.parameters import PARAMETRIZE_TYPES


def test_pydantic_serializer_without_model_error():
    class InvalidSerializerNoModel(PydanticSerializer):
        pass

    with pytest.raises(AttributeError) as exc:
        InvalidSerializerNoModel()

    assert exc.value.args[0] == (
        'Meta class attribute "pydantic_model" is mandatory for this serializer'
    )


def test_pydantic_serializer_invalid_model_error():
    class InvalidSerializerInvalidModel(PydanticSerializer):
        pydantic_model = object

    with pytest.raises(AttributeError) as exc:
        InvalidSerializerInvalidModel()

    assert exc.value.args[0] == (
        'Meta class attribute "pydantic_model" must be an instance of pydantic.BaseModel'
    )


def test_pydantic_model_serializer_successful_initialization(pydantic_model_test_serializer):
    pydantic_model_test_serializer()

    assert True  # exception was not thrown


def test_pydantic_model_serializer_to_internal_value(
    pydantic_model_test_serializer,
    pydantic_test_model,
    pydantic_test_model_data,
    serialized_pydantic_test_model_data,
):
    serializer = pydantic_model_test_serializer()

    internal_data = serializer.to_internal_value(pydantic_test_model_data)

    assert isinstance(internal_data, pydantic_test_model)
    assert internal_data.dict() == serialized_pydantic_test_model_data


@pytest.mark.parametrize(
    'argtype', ['serializer', 'model', 'dict'], ids=['with_serializer', 'with_model', 'with_dict']
)
def test_pydantic_model_serializer_to_representation_success(
    argtype,
    pydantic_model_test_serializer,
    pydantic_test_model,
    pydantic_test_model_data,
    serialized_pydantic_test_model_data,
):
    serializer = pydantic_model_test_serializer()
    argtype_mapping = {
        'serializer': pydantic_model_test_serializer(data=pydantic_test_model_data),
        'model': pydantic_test_model(**pydantic_test_model_data),
        'dict': pydantic_test_model_data,
    }

    representation = serializer.to_representation(argtype_mapping[argtype])

    assert representation == serialized_pydantic_test_model_data


def test_pydantic_model_serializer_to_representation_type_error(pydantic_model_test_serializer):
    serializer = pydantic_model_test_serializer()

    with pytest.raises(TypeError) as exc:
        serializer.to_representation('foo')

    assert exc.value.args[0] == 'Unknown type of instance for representation'


def test_pydantic_model_serializer_is_valid_success(
    pydantic_model_test_serializer, pydantic_test_model_data, serialized_pydantic_test_model_data
):
    serializer = pydantic_model_test_serializer(data=pydantic_test_model_data)

    valid = serializer.is_valid()

    assert valid is True
    assert serializer.data == serialized_pydantic_test_model_data
    assert serializer.errors == {}


def test_pydantic_model_serializer_is_valid_success_case_with_query_params(
    pydantic_test_query_serializer, serialized_pydantic_test_with_query
):
    query_string = 'any_str=hi&my_int=10&any_list=1&any_json={"foo": "bar"}&any_list=2&any_bool=true&any_str_list=one'
    query_dict = QueryDict(query_string)
    serializer = pydantic_test_query_serializer(data=query_dict)

    serializer_is_valid = serializer.is_valid(raise_exception=True)

    assert serializer_is_valid is True
    assert serializer.validated_data == serialized_pydantic_test_with_query
    assert serializer.errors == {}


def test_pydantic_model_serializer_is_valid_with_query_params__error_case_wrong_alias(
    pydantic_test_query_serializer,
):
    query_string = 'any_str=hi&any_int=10&any_list=1&any_json={"foo": "bar"}&any_list=2&any_bool=true&any_str_list=one'
    query_dict = QueryDict(query_string)

    serializer = pydantic_test_query_serializer(data=query_dict)

    with pytest.raises(expected_exception=ValidationError, match='field required'):
        serializer.is_valid(raise_exception=True)


def test_pydantic_model_serializer_is_valid_success_with_aliases(
    pydantic_model_with_aliases_test_serializer,
    pydantic_test_model_with_aliases_data,
    serialized_pydantic_test_model_with_aliases_data,
):
    serializer = pydantic_model_with_aliases_test_serializer(
        data=pydantic_test_model_with_aliases_data
    )

    valid = serializer.is_valid()

    assert valid is True
    assert serializer.data == serialized_pydantic_test_model_with_aliases_data
    assert serializer.errors == {}


def test_pydantic_model_serializer_is_valid_errors(pydantic_model_test_serializer):
    corrupted_data = {'field_a': 1, 'field_b': 'wrong type', 'created_at': 'wrong type'}
    serializer = pydantic_model_test_serializer(data=corrupted_data)

    valid = serializer.is_valid()

    assert valid is False
    assert serializer.errors == {
        'created_at': 'invalid datetime format',
        'field_a': 'str type expected',
        'field_b': 'value is not a valid integer',
    }


def test_pydantic_model_serializer_list(
    pydantic_model_test_serializer, pydantic_test_model_data, serialized_pydantic_test_model_data
):
    list_data = [pydantic_test_model_data, pydantic_test_model_data.copy()]
    expected_data = [
        serialized_pydantic_test_model_data,
        serialized_pydantic_test_model_data.copy(),
    ]
    serializer = pydantic_model_test_serializer(data=list_data, many=True)

    valid = serializer.is_valid()

    assert valid is True
    assert isinstance(serializer, ListSerializer)
    assert isinstance(serializer.child, pydantic_model_test_serializer)
    assert serializer.data == expected_data


def test_pydantic_django_model_serializer_successful_initialization(
    pydantic_django_model_test_serializer,
):
    pydantic_django_model_test_serializer()

    assert True  # exception was not thrown


def test_pydantic_django_model_serializer_initialization_case_with_out_query_params(
    pydantic_django_model_test_serializer, mocked__query_dict_to_dict
):
    pydantic_django_model_test_serializer()

    mocked__query_dict_to_dict.assert_not_called()


def test_pydantic_django_model_serializer_initialization__case_with_query_params(
    mocked__query_dict_to_dict, pydantic_test_query_serializer
):
    query_string = 'any_str=hi&any_int=10&any_list=1&any_json={"foo": "bar"}&any_list=2&any_bool=true&any_str_list=one'
    query_dict = QueryDict(query_string)
    pydantic_test_query_serializer(data=query_dict)

    mocked__query_dict_to_dict.assert_called_once_with(data=query_dict)


def test_pydantic_django_model_serializer_invalid_fields_subset_error(
    pydantic_django_model_test_serializer,
):
    class InvalidPydanticModel(BaseModel):
        class Config:
            orm_mode = True

        field_a: str
        field_c: int

    pydantic_django_model_test_serializer.Meta.pydantic_model = InvalidPydanticModel

    with pytest.raises(
        ImproperlyConfigured, match='Pydantic model fields is not subset of django model fields'
    ):
        pydantic_django_model_test_serializer()


def test_pydantic_django_model_serializer_meta_fields_error(pydantic_django_model_test_serializer):
    pydantic_django_model_test_serializer.Meta.fields = ['field_a']

    with pytest.raises(
        ImproperlyConfigured,
        match='Meta.fields does not affect this serializer behavior. Remove this attribute',
    ):
        pydantic_django_model_test_serializer()


def test_pydantic_django_model_serializer_orm_mode_disabled_error(
    pydantic_django_model_test_serializer,
):
    class InvalidPydanticModel(BaseModel):
        field_a: str

    pydantic_django_model_test_serializer.Meta.pydantic_model = InvalidPydanticModel

    with pytest.raises(
        ImproperlyConfigured,
        match='pydantic_model.Config.orm_mode must be True for this serializer',
    ):
        pydantic_django_model_test_serializer()


def test_pydantic_django_model_serializer_to_representation_success(
    pydantic_django_model_test_serializer,
    django_test_model,
    pydantic_test_model_data,
    serialized_pydantic_test_model_data,
):
    model_instance = django_test_model(**pydantic_test_model_data)

    representation = pydantic_django_model_test_serializer().to_representation(model_instance)

    assert representation == serialized_pydantic_test_model_data


def test_pydantic_django_model_serializer_create_success(
    pydantic_django_model_test_serializer,
    django_test_model,
    pydantic_test_model_data,
    serialized_pydantic_test_model_data,
):
    serializer = pydantic_django_model_test_serializer(data=pydantic_test_model_data)

    serializer.is_valid()
    serializer.create(serializer.data)

    django_test_model._meta.default_manager.create.assert_called_once_with(
        **serialized_pydantic_test_model_data
    )


def test_pydantic_django_model_serializer_update_success(
    pydantic_django_model_test_serializer,
    django_test_model,
    pydantic_test_model_data,
    serialized_pydantic_test_model_data,
):
    serializer = pydantic_django_model_test_serializer(data=pydantic_test_model_data)
    model_instance = django_test_model(**pydantic_test_model_data)
    model_instance.field_b = 100500

    serializer.is_valid()
    serializer.update(model_instance, serializer.data)

    assert model_instance.field_b == serialized_pydantic_test_model_data['field_b']
    model_instance.save.assert_called_once()


def test_pydantic_model_serializer__query_dict_to_dict(
    mocked__is_sequence_field, pydantic_shot_test_query_serializer
):
    query_string = 'any_str=hi&any_int=5'
    query_dict = QueryDict(query_string)
    mocked__is_sequence_field.return_value = False
    serializer = pydantic_shot_test_query_serializer(data=query_dict)
    mocked__is_sequence_field_calls = (call(field_type=str), call(field_type=int))

    test_result = serializer.query_dict_to_dict(data=query_dict)

    assert test_result == {'any_str': 'hi', 'any_int': '5'}
    mocked__is_sequence_field.assert_has_calls(calls=mocked__is_sequence_field_calls)


@pytest.mark.parametrize(('field_type', 'expected_result'), PARAMETRIZE_TYPES)
def test_pydantic_model_serializer__is_sequence_field(
    pydantic_test_query_serializer, field_type, expected_result
):
    query_string = 'any_str=hi&any_int=10&any_list=1&any_json={"foo": "bar"}&any_list=2&any_bool=true&any_str_list=one'
    query_dict = QueryDict(query_string)
    serializer = pydantic_test_query_serializer(data=query_dict)

    test_result = serializer._is_sequence_field(field_type=field_type)

    assert test_result is expected_result


@pytest.mark.parametrize(
    ('field_type', 'expected_result'),
    [(None, False), (str, True), (bytes, True), (bytearray, True), (dict, False), (object, False)],
)
def test_pydantic_model_serializer__is_string_like_field(
    pydantic_test_query_serializer, field_type, expected_result
):
    query_string = 'any_str=hi&any_int=10&any_list=1&any_json={"foo": "bar"}&any_list=2&any_bool=true&any_str_list=one'
    query_dict = QueryDict(query_string)
    serializer = pydantic_test_query_serializer(data=query_dict)

    test_result = serializer._is_string_like_field(field_type=field_type)

    assert test_result is expected_result

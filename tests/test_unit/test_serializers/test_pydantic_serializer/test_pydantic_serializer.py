from __future__ import annotations

import pytest
from rest_framework.serializers import ListSerializer

from restdoctor.rest_framework.serializers import PydanticSerializer


def test_pydantic_serializer_without_model_error():
    class InvalidSerializerNoModel(PydanticSerializer):
        pass

    with pytest.raises(AttributeError) as exc:
        InvalidSerializerNoModel()

    assert exc.value.args[0] == (
        'Class attribute "pydantic_model" is mandatory for this serializer'
    )


def test_pydantic_serializer_invalid_model_error():
    class InvalidSerializerInvalidModel(PydanticSerializer):
        pydantic_model = object

    with pytest.raises(AttributeError) as exc:
        InvalidSerializerInvalidModel()

    assert exc.value.args[0] == (
        'Class attribute "pydantic_model" must be an instance of pydantic.BaseModel'
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

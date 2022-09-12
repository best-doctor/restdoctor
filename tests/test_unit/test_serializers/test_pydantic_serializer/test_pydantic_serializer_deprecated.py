from __future__ import annotations

import pytest
from django.core.exceptions import ImproperlyConfigured
from pydantic import BaseModel
from rest_framework.serializers import ListSerializer


def test_pydantic_model_serializer_successful_initialization_depreacated(
    pydantic_model_test_serializer_deprecated,
):
    pydantic_model_test_serializer_deprecated()

    assert True  # exception was not thrown


def test_pydantic_model_serializer_to_internal_value_deprecated(
    pydantic_model_test_serializer_deprecated,
    pydantic_test_model,
    pydantic_test_model_data,
    serialized_pydantic_test_model_data,
):
    serializer = pydantic_model_test_serializer_deprecated()

    internal_data = serializer.to_internal_value(pydantic_test_model_data)

    assert isinstance(internal_data, pydantic_test_model)
    assert internal_data.dict() == serialized_pydantic_test_model_data


@pytest.mark.parametrize(
    'argtype', ['serializer', 'model', 'dict'], ids=['with_serializer', 'with_model', 'with_dict']
)
def test_pydantic_model_serializer_to_representation_success_deprecated(
    argtype,
    pydantic_model_test_serializer_deprecated,
    pydantic_test_model,
    pydantic_test_model_data,
    serialized_pydantic_test_model_data,
):
    serializer = pydantic_model_test_serializer_deprecated()
    argtype_mapping = {
        'serializer': pydantic_model_test_serializer_deprecated(data=pydantic_test_model_data),
        'model': pydantic_test_model(**pydantic_test_model_data),
        'dict': pydantic_test_model_data,
    }

    representation = serializer.to_representation(argtype_mapping[argtype])

    assert representation == serialized_pydantic_test_model_data


def test_pydantic_model_serializer_to_representation_type_error_deprecated(
    pydantic_model_test_serializer_deprecated,
):
    serializer = pydantic_model_test_serializer_deprecated()

    with pytest.raises(TypeError) as exc:
        serializer.to_representation('foo')

    assert exc.value.args[0] == 'Unknown type of instance for representation'


def test_pydantic_model_serializer_is_valid_success_deprecated(
    pydantic_model_test_serializer_deprecated,
    pydantic_test_model_data,
    serialized_pydantic_test_model_data,
):
    serializer = pydantic_model_test_serializer_deprecated(data=pydantic_test_model_data)

    valid = serializer.is_valid()

    assert valid is True
    assert serializer.data == serialized_pydantic_test_model_data
    assert serializer.errors == {}


def test_pydantic_model_serializer_is_valid_success_with_aliases_deprecated(
    pydantic_model_with_aliases_test_serializer_deprecated,
    pydantic_test_model_with_aliases_data,
    serialized_pydantic_test_model_with_aliases_data,
):
    serializer = pydantic_model_with_aliases_test_serializer_deprecated(
        data=pydantic_test_model_with_aliases_data
    )

    valid = serializer.is_valid()

    assert valid is True
    assert serializer.data == serialized_pydantic_test_model_with_aliases_data
    assert serializer.errors == {}


def test_pydantic_model_serializer_is_valid_errors_deprecated(
    pydantic_model_test_serializer_deprecated,
):
    corrupted_data = {'field_a': 1, 'field_b': 'wrong type', 'created_at': 'wrong type'}
    serializer = pydantic_model_test_serializer_deprecated(data=corrupted_data)

    valid = serializer.is_valid()

    assert valid is False
    assert serializer.errors == {
        'created_at': 'invalid datetime format',
        'field_a': 'str type expected',
        'field_b': 'value is not a valid integer',
    }


def test_pydantic_model_serializer_list_deprecated(
    pydantic_model_test_serializer_deprecated,
    pydantic_test_model_data,
    serialized_pydantic_test_model_data,
):
    list_data = [pydantic_test_model_data, pydantic_test_model_data.copy()]
    expected_data = [
        serialized_pydantic_test_model_data,
        serialized_pydantic_test_model_data.copy(),
    ]
    serializer = pydantic_model_test_serializer_deprecated(data=list_data, many=True)

    valid = serializer.is_valid()

    assert valid is True
    assert isinstance(serializer, ListSerializer)
    assert isinstance(serializer.child, pydantic_model_test_serializer_deprecated)
    assert serializer.data == expected_data


def test_pydantic_django_model_serializer_successful_initialization_deprecated(
    pydantic_django_model_test_serializer_deprecated,
):
    pydantic_django_model_test_serializer_deprecated()

    assert True  # exception was not thrown


def test_pydantic_django_model_serializer_invalid_fields_subset_error_deprecated(
    pydantic_django_model_test_serializer_deprecated,
):
    class InvalidPydanticModel(BaseModel):
        class Config:
            orm_mode = True

        field_a: str
        field_c: int

    pydantic_django_model_test_serializer_deprecated.pydantic_model = InvalidPydanticModel

    with pytest.raises(
        ImproperlyConfigured, match='Pydantic model fields is not subset of django model fields'
    ):
        pydantic_django_model_test_serializer_deprecated()


def test_pydantic_django_model_serializer_meta_fields_error_deprecated(
    pydantic_django_model_test_serializer_deprecated,
):
    pydantic_django_model_test_serializer_deprecated.Meta.fields = ['field_a']

    with pytest.raises(
        ImproperlyConfigured,
        match='Meta.fields does not affect this serializer behavior. Remove this attribute',
    ):
        pydantic_django_model_test_serializer_deprecated()


def test_pydantic_django_model_serializer_orm_mode_disabled_error_deprecated(
    pydantic_django_model_test_serializer_deprecated,
):
    class InvalidPydanticModel(BaseModel):
        field_a: str

    pydantic_django_model_test_serializer_deprecated.pydantic_model = InvalidPydanticModel

    with pytest.raises(
        ImproperlyConfigured,
        match='pydantic_model.Config.orm_mode must be True for this serializer',
    ):
        pydantic_django_model_test_serializer_deprecated()


def test_pydantic_django_model_serializer_to_representation_success_deprecated(
    pydantic_django_model_test_serializer_deprecated,
    django_test_model,
    pydantic_test_model_data,
    serialized_pydantic_test_model_data,
):
    model_instance = django_test_model(**pydantic_test_model_data)

    representation = pydantic_django_model_test_serializer_deprecated().to_representation(
        model_instance
    )

    assert representation == serialized_pydantic_test_model_data


def test_pydantic_django_model_serializer_create_success_deprecated(
    pydantic_django_model_test_serializer_deprecated,
    django_test_model,
    pydantic_test_model_data,
    serialized_pydantic_test_model_data,
):
    serializer = pydantic_django_model_test_serializer_deprecated(data=pydantic_test_model_data)

    serializer.is_valid()
    serializer.create(serializer.data)

    django_test_model._meta.default_manager.create.assert_called_once_with(
        **serialized_pydantic_test_model_data
    )


def test_pydantic_django_model_serializer_update_success_deprecated(
    pydantic_django_model_test_serializer_deprecated,
    django_test_model,
    pydantic_test_model_data,
    serialized_pydantic_test_model_data,
):
    serializer = pydantic_django_model_test_serializer_deprecated(data=pydantic_test_model_data)
    model_instance = django_test_model(**pydantic_test_model_data)
    model_instance.field_b = 100500

    serializer.is_valid()
    serializer.update(model_instance, serializer.data)

    assert model_instance.field_b == serialized_pydantic_test_model_data['field_b']
    model_instance.save.assert_called_once()

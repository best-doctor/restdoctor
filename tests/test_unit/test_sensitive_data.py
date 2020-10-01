import pytest


from restdoctor.django.sensitive_data import get_model_sensitive_fields, is_model_field_sensitive
from restdoctor.rest_framework.sensitive_data import (
    get_serializer_sensitive_fields, get_serializer_instance, get_serializer_sensitive_data_config,
    get_field_serializer, clear_sensitive_data,
)
from tests.test_unit.stubs import (
    ParentSensitiveDataModel, ModelWithoutSensitiveData,
    SerializerWithSensitiveData, SerializerWithoutSensitiveData, ModelSerializerWithSensitiveData,
)

@pytest.mark.parametrize(
    ('model', 'expected_result'),
    (
        (ParentSensitiveDataModel, ['title']),
        (ModelWithoutSensitiveData, []),
    ),
)
def test_get_model_sensitive_fields(model, expected_result):
    result = get_model_sensitive_fields(model)

    assert result == expected_result


@pytest.mark.parametrize(
    ('model', 'field_path', 'expected_result'),
    (
        (ParentSensitiveDataModel, 'title.test.test', False),
        (ParentSensitiveDataModel, 'test', False),
        (ParentSensitiveDataModel, 'field_fk', False),
        (ParentSensitiveDataModel, 'title', True),
        (ParentSensitiveDataModel, 'field_fk.title', True),
        (ParentSensitiveDataModel, 'field_fk.field_fk.title', False),
        (ParentSensitiveDataModel, 'field_m2m.title', True),
        (ParentSensitiveDataModel, 'field_o2o.title', True),
    ),
)
def test_is_model_field_sensitive(model, field_path, expected_result):
    result = is_model_field_sensitive(model, field_path)

    assert result == expected_result


@pytest.mark.parametrize(
    ('serializer', 'with_model_sensitive_fields', 'expected_result'),
    (
        (SerializerWithoutSensitiveData, True, []),
        (SerializerWithoutSensitiveData, False, []),
        (SerializerWithSensitiveData, True, ['field1', 'field2']),
        (SerializerWithSensitiveData, False, ['field1', 'field2']),
        (ModelSerializerWithSensitiveData, True, ['first_name', 'last_name', 'title']),
        (ModelSerializerWithSensitiveData, False, ['first_name', 'last_name']),
    ),
)
def test_get_serializer_sensitive_fields(serializer, with_model_sensitive_fields, expected_result):
    result = get_serializer_sensitive_fields(
        serializer=serializer, with_model_sensitive_fields=with_model_sensitive_fields)

    assert result == expected_result


@pytest.mark.parametrize(
    'serializer',
    (SerializerWithSensitiveData, SerializerWithSensitiveData()),
)
def test_get_serializer_instance(serializer):
    result = get_serializer_instance(serializer)

    assert isinstance(result, SerializerWithSensitiveData)


@pytest.mark.parametrize(
    ('field_name', 'field'),
    (
        ('field1', ModelSerializerWithSensitiveData().fields['field1']),
        ('field2', ModelSerializerWithSensitiveData().fields['field2']),
        ('field3', ModelSerializerWithSensitiveData().fields['field3']),
    ),
)
def test_get_field_serializer(field_name, field):
    result = get_field_serializer(ModelSerializerWithSensitiveData(), field_name, field)

    assert isinstance(result, SerializerWithSensitiveData)


def test_get_serializer_sensitive_data_config():
    result = get_serializer_sensitive_data_config(ModelSerializerWithSensitiveData())

    assert result == {
        'first_name': True,
        'last_name': True,
        'title': True,
        'field1': {'field1': True, 'field2': True},
        'field2': {'field1': True, 'field2': True},
        'field3': {'field1': True, 'field2': True},
    }


@pytest.mark.parametrize(
    'data, expected_data',
    (
        ({'first_name': 'Иван', 'id': 1}, {'first_name': '[Cleaned]', 'id': 1}),
        ({'last_name': 'Иванович', 'id': 1}, {'last_name': '[Cleaned]', 'id': 1}),
        (
            [{'first_name': 'Иван', 'id': 1}, {'first_name': 'Петр', 'id': 2}],
            [{'first_name': '[Cleaned]', 'id': 1}, {'first_name': '[Cleaned]', 'id': 2}],
        ),
        (
            {'field1': {'field1': 'Иван', 'id': 1}, 'id': 1},
            {'field1': {'field1': '[Cleaned]', 'id': 1}, 'id': 1},
        ),
    ),
)
def test_clear_sensitive_data(data, expected_data):
    result = clear_sensitive_data(data, ModelSerializerWithSensitiveData())

    assert result == expected_data

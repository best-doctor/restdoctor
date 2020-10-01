import pytest
from django.core.validators import URLValidator
from rest_framework.fields import (
    Field, ReadOnlyField, IntegerField, CharField, EmailField,
    RegexField, URLField, UUIDField,
)

from restdoctor.rest_framework.schema import RestDoctorSchema


@pytest.mark.parametrize(
    'field,expected_schema',
    (
        (Field(), {'type': 'string'}),
        (ReadOnlyField(), {'readOnly': True, 'type': 'string'}),
        (Field(write_only=True), {'writeOnly': True, 'type': 'string'}),
        (Field(allow_null=True), {'nullable': True, 'type': 'string'}),
        (Field(default='default'), {'default': 'default', 'type': 'string'}),
        (Field(help_text='help_text'), {'description': 'help_text', 'type': 'string'}),
    ),
)
def test_basic_fields_schema(field, expected_schema):
    schema = RestDoctorSchema()

    result = schema._get_field_schema(field)

    assert result == expected_schema


@pytest.mark.parametrize(
    'field,expected_schema',
    (
        (IntegerField(min_value=100, max_value=200), {'type': 'integer', 'minimum': 100, 'maximum': 200}),
        (IntegerField(max_value=2147483648), {'type': 'integer', 'maximum': 2147483648, 'format': 'int64'}),
        (CharField(min_length=5, max_length=10), {'type': 'string', 'minLength': 5, 'maxLength': 10}),
        (EmailField(), {'type': 'string', 'format': 'email'}),
        (RegexField('pattern'), {'type': 'string', 'pattern': 'pattern'}),
        (URLField(), {'type': 'string', 'format': 'uri', 'pattern': URLValidator.regex.pattern}),
        (UUIDField(), {'type': 'string', 'format': 'uuid'}),
    ),
)
def test_fields_validators_schema(field, expected_schema):
    schema = RestDoctorSchema()

    result = schema._get_field_schema(field)

    assert result == expected_schema

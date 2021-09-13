from __future__ import annotations

import decimal
import re

import pytest
from django.core.validators import MaxValueValidator, MinValueValidator, URLValidator
from rest_framework import serializers
from rest_framework.fields import (
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    DecimalField,
    DurationField,
    EmailField,
    Field,
    FileField,
    FloatField,
    ImageField,
    IntegerField,
    IPAddressField,
    JSONField,
    ReadOnlyField,
    RegexField,
    SlugField,
    TimeField,
    URLField,
    UUIDField,
)
from rest_framework_gis.fields import GeometryField

from restdoctor.rest_framework.schema import RestDoctorSchema

url_pattern = URLValidator.regex.pattern.replace('\\Z', '\\z')


@pytest.mark.parametrize(
    ('field', 'expected_schema'),
    [
        (Field(), {'type': 'string'}),
        (ReadOnlyField(), {'readOnly': True, 'type': 'string'}),
        (Field(write_only=True), {'writeOnly': True, 'type': 'string'}),
        (Field(allow_null=True), {'nullable': True, 'type': 'string'}),
        (Field(default='default'), {'default': 'default', 'type': 'string'}),
        (Field(help_text='help_text'), {'description': 'help_text', 'type': 'string'}),
    ],
)
def test_basic_fields_schema(field, expected_schema):
    schema = RestDoctorSchema()

    result = schema._get_field_schema(field)

    assert result == expected_schema


@pytest.mark.parametrize(
    ('field', 'expected_schema'),
    [
        (
            # AutoField, BigIntegerField, IntegerField, PositiveIntegerField,
            # PositiveSmallIntegerField, SmallIntegerField
            IntegerField(validators=[MinValueValidator(10)]),
            {'type': 'integer', 'minimum': 10},
        ),
        (
            # BigIntegerField
            IntegerField(max_value=2 ** 32),
            {'type': 'integer', 'maximum': 2 ** 32, 'format': 'int64'},
        ),
        (
            # PositiveIntegerField, PositiveSmallIntegerField
            IntegerField(min_value=0),
            {'type': 'integer', 'minimum': 0},
        ),
        (
            # BooleanField, NullBooleanField
            BooleanField(),
            {'type': 'boolean'},
        ),
        (
            # NullBooleanField
            BooleanField(allow_null=True),
            {'type': 'boolean', 'nullable': True},
        ),
        (
            # CharField, TextField
            CharField(allow_blank=True, max_length=10, min_length=2),
            {'type': 'string', 'maxLength': 10, 'minLength': 2},
        ),
        (
            # CharField, TextField
            CharField(allow_blank=False),
            {'type': 'string'},
        ),
        (
            # CharField, TextField
            CharField(trim_whitespace=False),
            {'type': 'string'},
        ),
        (
            # DateField
            DateField(),
            {'type': 'string', 'format': 'date'},
        ),
        (
            # DateTimeField
            DateTimeField(),
            {'type': 'string', 'format': 'date-time'},
        ),
        (
            # DecimalField
            DecimalField(
                max_digits=4,
                decimal_places=2,
                validators=[MinValueValidator(10), MaxValueValidator(20)],
            ),
            {
                'type': 'string',
                'format': 'decimal',
                'multipleOf': 0.01,
                'maximum': 20,
                'minimum': 10,
            },
        ),
        (
            # DecimalField
            DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)]),
            {
                'type': 'string',
                'format': 'decimal',
                'multipleOf': 0.01,
                'maximum': 1000,
                'minimum': 0,
            },
        ),
        (
            # DecimalField decimal
            DecimalField(
                max_digits=5,
                decimal_places=2,
                validators=[
                    MinValueValidator(decimal.Decimal('0.1')),
                    MaxValueValidator(decimal.Decimal('2.1222')),
                ],
            ),
            {
                'type': 'string',
                'format': 'decimal',
                'multipleOf': 0.01,
                'maximum': 2.1222,
                'minimum': 0.1,
            },
        ),
        (
            # DurationField
            DurationField(max_value=300, min_value=100),
            {'type': 'string', 'maximum': 300, 'minimum': 100},
        ),
        (
            # EmailField
            EmailField(),
            {'type': 'string', 'format': 'email'},
        ),
        (
            # JSONField
            JSONField(),
            {'type': 'object'},
        ),
        (
            # FileField
            FileField(),
            {'type': 'string', 'format': 'binary'},
        ),
        (
            # FloatField
            FloatField(),
            {'type': 'number'},
        ),
        (
            # ImageField
            ImageField(),
            {'type': 'string', 'format': 'binary'},
        ),
        (
            # SlugField
            SlugField(),
            {'type': 'string', 'pattern': '^[-a-zA-Z0-9_]+$'},
        ),
        (
            # TimeField
            TimeField(),
            {'type': 'string'},
        ),
        (
            # URLField
            URLField(),
            {'type': 'string', 'format': 'uri', 'pattern': url_pattern},
        ),
        (
            # UUIDField
            UUIDField(),
            {'type': 'string', 'format': 'uuid'},
        ),
        (
            # IPAddressField
            IPAddressField(protocol='IPv6'),
            {'type': 'string', 'format': 'ipv6'},
        ),
        (
            RegexField(re.compile(r'^[-a-zA-Z0-9_]+$')),
            {'type': 'string', 'pattern': '^[-a-zA-Z0-9_]+$'},
        ),
        (
            # IPAddressField
            IPAddressField(protocol='IPv4'),
            {'type': 'string', 'format': 'ipv4'},
        ),
        (
            IntegerField(min_value=100, max_value=200),
            {'type': 'integer', 'minimum': 100, 'maximum': 200},
        ),
        (
            IntegerField(max_value=2147483648),
            {'type': 'integer', 'maximum': 2147483648, 'format': 'int64'},
        ),
        (
            CharField(min_length=5, max_length=10),
            {'type': 'string', 'minLength': 5, 'maxLength': 10},
        ),
        (
            GeometryField(),
            {
                'type': 'object',
                'required': ['type', 'coordinates'],
                'properties': {
                    'type': {'type': 'string', 'enum': ['Point']},
                    'coordinates': {
                        'type': 'array',
                        'items': {'type': 'number', 'format': 'float'},
                        'example': [12.9721, 77.5933],
                        'minItems': 2,
                        'maxItems': 3,
                    },
                },
            },
        ),
    ],
)
def test_fields_validators_schema(field, expected_schema):
    schema = RestDoctorSchema()

    result = schema._get_field_schema(field)

    assert result == expected_schema

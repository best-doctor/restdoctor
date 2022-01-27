from __future__ import annotations

import pytest
from django.core.validators import URLValidator
from django_filters import (
    BooleanFilter,
    ChoiceFilter,
    MultipleChoiceFilter,
    TypedChoiceFilter,
    TypedMultipleChoiceFilter,
    DateFilter,
    DateFromToRangeFilter,
    DateTimeFilter,
    DateTimeFromToRangeFilter,
    NumberFilter,
    TimeFilter,
    ModelChoiceFilter,
    ModelMultipleChoiceFilter,
)
from django_filters.rest_framework import BooleanFilter as RestBooleanFilter
from rest_framework import ISO_8601

from restdoctor.rest_framework.schema.filters import get_filter_schema, FILTER_MAP

url_pattern = URLValidator.regex.pattern.replace('\\Z', '\\z')


@pytest.mark.parametrize(
    ('field', 'expected_schema'),
    [
        (BooleanFilter(), {'type': 'boolean'}),
        (RestBooleanFilter(), {'type': 'boolean'}),
        (
            ChoiceFilter(choices=((1, 1), (2, 2)), empty_label=None),
            {'type': 'integer', 'enum': [1, 2]},
        ),
        (
            MultipleChoiceFilter(choices=((False, False), (True, True))),
            {'type': 'boolean', 'enum': [False, True]},
        ),
        (TypedChoiceFilter(choices=((1.1, 1.1), (2, 2))), {'type': 'number', 'enum': [1.1, 2]}),
        (
            TypedMultipleChoiceFilter(choices=(('a', 'a'), ('b', 'b'))),
            {'type': 'string', 'enum': ['a', 'b']},
        ),
        (DateFilter(), {'type': 'string', 'format': 'date', 'example': '2022-01-31'}),
        (
            DateFilter(input_formats=['%Y-%m']),
            {'type': 'string', 'format': 'date', 'example': '2022-01'},
        ),
        (DateFromToRangeFilter(), {'type': 'string', 'format': 'date'}),
        (
            DateTimeFilter(),
            {'type': 'string', 'format': 'date-time', 'example': '2022-01-31 11:22:33'},
        ),
        (
            DateTimeFilter(input_formats=[ISO_8601]),
            {
                'type': 'string',
                'format': 'date-time',
                'example': '2022-01-31T11:22:33.000000+00:00',
            },
        ),
        (
            DateTimeFilter(input_formats=['%Y-%m-%dT%H %M %S %z']),
            {'type': 'string', 'format': 'date-time', 'example': '2022-01-31T11 22 33 +0000'},
        ),
        (DateTimeFromToRangeFilter(), {'type': 'string', 'format': 'date-time'}),
        (NumberFilter(), {'type': 'number'}),
        (TimeFilter(), {'type': 'string', 'format': 'time', 'example': '11:22:33'}),
        (TimeFilter(input_formats=['%H %M %S %f']), {'type': 'string', 'format': 'time', 'example': '11 22 33 000000'}),
        (ModelChoiceFilter(), {'type': 'string'}),
        (ModelMultipleChoiceFilter(), {'type': 'string'}),
    ],
)
def test__get_filter_schema(field, expected_schema):
    result = get_filter_schema(filter_field=field, filter_map=FILTER_MAP)

    assert result == expected_schema


class CustomDateFilter(DateFilter):
    pass


def test__get_filter_schema__custom_field():
    result = get_filter_schema(
        filter_field=CustomDateFilter(),
        filter_map={**FILTER_MAP, CustomDateFilter: {'type': 'custom-date'}},
    )

    assert result == {'type': 'custom-date'}

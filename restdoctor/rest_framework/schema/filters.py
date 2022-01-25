from __future__ import annotations

import datetime
import decimal
import functools
import typing

from django_filters import (
    Filter,
    BooleanFilter,
    ChoiceFilter,
    DateFilter,
    DateFromToRangeFilter,
    DateTimeFilter,
    DateTimeFromToRangeFilter,
    NumberFilter,
    TimeFilter,
    TypedChoiceFilter,
    MultipleChoiceFilter,
    TypedMultipleChoiceFilter,
    ModelChoiceFilter,
    ModelMultipleChoiceFilter,
)
from rest_framework import ISO_8601

from restdoctor.utils.custom_types import FilterMap


def _get_filter_schema_choice(
    filter_field: typing.Union[
        ChoiceFilter, MultipleChoiceFilter, TypedChoiceFilter, TypedMultipleChoiceFilter
    ]
) -> dict:
    choice_type = 'string'

    try:
        choices = filter_field.field.choices
    except KeyError:
        return {'type': choice_type}

    choice_keys = [c for c, _ in choices]
    for type_, repr_ in (
        (bool, 'boolean'),
        (int, 'integer'),
        ((int, float, decimal.Decimal), 'number'),
    ):
        if all(isinstance(choice, type_) for choice in choice_keys):  # type: ignore
            choice_type = repr_
            break

    return {'type': choice_type, 'enum': choice_keys}


def _get_filter_schema_datetime(
    filter_field: typing.Union[
        DateFilter, DateFromToRangeFilter, DateTimeFilter, DateTimeFromToRangeFilter
    ],
    schema_format: str,
) -> dict:
    schema = {'type': 'string', 'format': schema_format}
    input_formats = list(
        filter_field.extra.get(
            'input_formats', getattr(filter_field.field_class, 'input_formats', [])
        )
    )
    if input_formats:
        input_format = input_formats[0]
        example_datetime = datetime.datetime(2022, 1, 31, 11, 22, 33, tzinfo=datetime.timezone.utc)
        if input_format.lower() == ISO_8601:
            schema['example'] = example_datetime.isoformat(timespec='microseconds')
        else:
            schema['example'] = example_datetime.strftime(input_format)

    return schema


FILTER_MAP: FilterMap = {
    BooleanFilter: {'type': 'boolean'},
    ChoiceFilter: _get_filter_schema_choice,
    MultipleChoiceFilter: _get_filter_schema_choice,
    TypedChoiceFilter: _get_filter_schema_choice,
    TypedMultipleChoiceFilter: _get_filter_schema_choice,
    DateFilter: functools.partial(_get_filter_schema_datetime, schema_format='date'),
    DateFromToRangeFilter: functools.partial(_get_filter_schema_datetime, schema_format='date'),
    DateTimeFilter: functools.partial(_get_filter_schema_datetime, schema_format='date-time'),
    DateTimeFromToRangeFilter: functools.partial(
        _get_filter_schema_datetime, schema_format='date-time'
    ),
    NumberFilter: {'type': 'number'},
    TimeFilter: functools.partial(_get_filter_schema_datetime, schema_format='time'),
    ModelChoiceFilter: {'type': 'string'},
    ModelMultipleChoiceFilter: {'type': 'string'},
}


def get_filter_schema(filter_field: Filter, filter_map: FilterMap) -> dict:
    field_parents = type(filter_field).mro()

    schema: typing.Union[dict, typing.Callable] = {'type': 'string'}
    for field_parent in field_parents[:-1]:
        try:
            schema = filter_map[field_parent]
            break
        except KeyError:
            pass

    if callable(schema):
        return schema(filter_field)
    return schema

from __future__ import annotations

import decimal
import functools

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
)


@functools.singledispatch
def get_filter_schema(filter_field: Filter) -> dict:
    return {'type': 'string'}


@get_filter_schema.register
def _(filter_field: BooleanFilter) -> dict:
    return {'type': 'boolean'}


@get_filter_schema.register(ChoiceFilter)
@get_filter_schema.register(MultipleChoiceFilter)
@get_filter_schema.register(TypedChoiceFilter)
@get_filter_schema.register(TypedMultipleChoiceFilter)
def _(
    filter_field: ChoiceFilter
    | MultipleChoiceFilter
    | TypedChoiceFilter
    | TypedMultipleChoiceFilter,
) -> dict:
    choice_type = 'string'

    try:
        choices = filter_field.field.choices
    except KeyError:
        return {'type': choice_type}

    for type_, repr_ in (
        (bool, 'boolean'),
        (int, 'integer'),
        ((int, float, decimal.Decimal), 'number'),
    ):
        if all(isinstance(choice, type_) for choice, _ in choices):
            choice_type = repr_
            break

    return {'type': choice_type, 'enum': [c[0] for c in choices]}


@get_filter_schema.register(DateFilter)
@get_filter_schema.register(DateFromToRangeFilter)
def _(filter_field: DateFilter | DateFromToRangeFilter) -> dict:
    return {'type': 'string', 'format': 'date'}


@get_filter_schema.register(DateTimeFilter)
@get_filter_schema.register(DateTimeFromToRangeFilter)
def _(filter_field: DateTimeFilter | DateTimeFromToRangeFilter) -> dict:
    return {'type': 'string', 'format': 'date-time'}


@get_filter_schema.register
def _(filter_field: NumberFilter) -> dict:
    return {'type': 'number'}


@get_filter_schema.register
def _(filter_field: TimeFilter) -> dict:
    return {'type': 'string', 'format': 'time'}

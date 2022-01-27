from __future__ import annotations

import pytest
from django.core.exceptions import ImproperlyConfigured
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from restdoctor.rest_framework.schema import RestDoctorSchema
from restdoctor.rest_framework.schema.generators import RefsSchemaGenerator30, RefsSchemaGenerator31
from tests.test_unit.test_schema.stubs import (
    DefaultFilterSet,
    FilterSetWithLabels,
    FilterSetWithNoLabels,
    ListViewSetWithoutRequestSerializer,
    ListViewSetWithRequestSerializer,
)


@pytest.mark.parametrize(
    ('viewset', 'generator_class', 'expected_parameters'),
    [
        (
            ListViewSetWithRequestSerializer,
            RefsSchemaGenerator30,
            [
                {
                    'in': 'query',
                    'name': 'filter_uuid_field',
                    'required': False,
                    'schema': {'type': 'string', 'format': 'uuid'},
                },
                {
                    'in': 'query',
                    'name': 'filter_field',
                    'required': True,
                    'schema': {'type': 'string', 'nullable': True, 'description': 'Help text'},
                },
            ],
        ),
        (
            ListViewSetWithRequestSerializer,
            RefsSchemaGenerator31,
            [
                {
                    'in': 'query',
                    'name': 'filter_uuid_field',
                    'required': False,
                    'schema': {'type': 'string', 'format': 'uuid'},
                },
                {
                    'in': 'query',
                    'name': 'filter_field',
                    'required': True,
                    'schema': {'type': ['string', 'null'], 'description': 'Help text'},
                },
            ],
        ),
        (ListViewSetWithoutRequestSerializer, RefsSchemaGenerator30, []),
        (ListViewSetWithoutRequestSerializer, RefsSchemaGenerator31, []),
    ],
)
def test_schema_for_list_viewset(
    get_create_view_func, viewset, generator_class, expected_parameters
):
    create_view = get_create_view_func('test', viewset, 'test', generator_class=generator_class)

    view = create_view('/test/', 'GET')
    operation = view.schema.get_operation('/test/', 'GET')

    assert operation['parameters'] == expected_parameters


@pytest.mark.parametrize(
    ('viewset', 'generator_class', 'expected_parameters'),
    [
        (
            ListViewSetWithRequestSerializer,
            RefsSchemaGenerator30,
            [
                {
                    'in': 'query',
                    'name': 'filter_uuid_field',
                    'required': False,
                    'schema': {'type': 'string', 'format': 'uuid'},
                },
                {
                    'in': 'query',
                    'name': 'filter_field',
                    'required': True,
                    'schema': {'type': 'string', 'nullable': True, 'description': 'Help text'},
                },
            ],
        ),
        (
            ListViewSetWithRequestSerializer,
            RefsSchemaGenerator31,
            [
                {
                    'in': 'query',
                    'name': 'filter_uuid_field',
                    'required': False,
                    'schema': {'type': 'string', 'format': 'uuid'},
                },
                {
                    'in': 'query',
                    'name': 'filter_field',
                    'required': True,
                    'schema': {'type': ['string', 'null'], 'description': 'Help text'},
                },
            ],
        ),
        (ListViewSetWithoutRequestSerializer, RefsSchemaGenerator30, []),
        (ListViewSetWithoutRequestSerializer, RefsSchemaGenerator31, []),
    ],
)
def test_get_request_serializer_filter_parameters(
    get_create_view_func, viewset, generator_class, expected_parameters
):
    list_view = get_create_view_func('test', viewset, 'test', generator_class=generator_class)

    view = list_view('/test/', 'GET')
    parameters = view.schema.get_request_serializer_filter_parameters('/test/', 'GET')

    assert parameters == expected_parameters


@pytest.mark.parametrize(
    ('filter_backends', 'filterset_class', 'expected_parameters'),
    [
        (
            [DjangoFilterBackend, OrderingFilter],
            DefaultFilterSet,
            [
                {
                    'description': 'UUID',
                    'in': 'query',
                    'name': 'uuid',
                    'required': False,
                    'schema': {'type': 'string'},
                },
                {
                    'description': 'Another Event timestamp',
                    'in': 'query',
                    'name': 'timestamp',
                    'required': False,
                    'schema': {'type': 'string', 'format': 'date-time', 'example': '2022-01-31T11:22:33.000000+00:00'},
                },
                {
                    'description': 'Which field to use when ordering the results.',
                    'in': 'query',
                    'name': 'ordering',
                    'required': False,
                    'schema': {'type': 'string'},
                },
            ],
        ),
        (
            [DjangoFilterBackend],
            FilterSetWithNoLabels,
            [
                {
                    'description': 'UUID',
                    'in': 'query',
                    'name': 'uuid',
                    'required': False,
                    'schema': {'type': 'string'},
                },
                {
                    'description': 'Event timestamp',
                    'in': 'query',
                    'name': 'my_model__timestamp',
                    'required': False,
                    'schema': {'type': 'string', 'format': 'date-time', 'example': '2022-01-31T11:22:33.000000+00:00'},
                },
                {
                    'description': 'Event timestamp',
                    'in': 'query',
                    'name': 'my_model__timestamp__in',
                    'required': False,
                    'schema': {'type': 'string', 'format': 'date-time', 'example': '2022-01-31T11:22:33.000000+00:00'},
                },
                {
                    'description': 'my another one model',
                    'in': 'query',
                    'name': 'my_another_one_model__isnull',
                    'required': False,
                    'schema': {'type': 'boolean'},
                },
                {
                    'description': 'Another One Event timestamp',
                    'in': 'query',
                    'name': 'my_another_one_model__timestamp',
                    'required': False,
                    'schema': {'format': 'date-time', 'type': 'string', 'example': '2022-01-31T11:22:33.000000+00:00'},
                },
                {
                    'description': 'Another Event timestamp',
                    'in': 'query',
                    'name': 'created_at_date',
                    'required': False,
                    'schema': {'type': 'string', 'format': 'date', 'example': '2022-01-31'},
                },
                {
                    'description': 'created_after',
                    'in': 'query',
                    'name': 'created_after',
                    'required': False,
                    'schema': {'type': 'string', 'format': 'date', 'example': '2022-01-31'},
                },
            ],
        ),
        (
            [DjangoFilterBackend],
            FilterSetWithLabels,
            [
                {
                    'description': 'UUID',
                    'in': 'query',
                    'name': 'uuid',
                    'required': False,
                    'schema': {'type': 'string'},
                },
                {
                    'description': 'Event timestamp',
                    'in': 'query',
                    'name': 'my_model__timestamp',
                    'required': False,
                    'schema': {'format': 'date-time', 'type': 'string', 'example': '2022-01-31T11:22:33.000000+00:00'},
                },
                {
                    'description': 'Another One Event timestamp',
                    'in': 'query',
                    'name': 'my_another_one_model__timestamp',
                    'required': False,
                    'schema': {'format': 'date-time', 'type': 'string', 'example': '2022-01-31T11:22:33.000000+00:00'},
                },
                {
                    'description': 'Created At Timestamp Label',
                    'in': 'query',
                    'name': 'created_at_date',
                    'required': False,
                    'schema': {'format': 'date', 'type': 'string', 'example': '2022-01-31'},
                },
                {
                    'description': 'Custom Method Label',
                    'in': 'query',
                    'name': 'created_after',
                    'required': False,
                    'schema': {'format': 'date', 'type': 'string', 'example': '2022-01-31'},
                },
            ],
        ),
    ],
)
def test_schema_for_viewset_with_filter_backend(
    get_create_view_func,
    viewset_with_filter_backends_factory,
    filter_backends,
    filterset_class,
    expected_parameters,
):
    viewset = viewset_with_filter_backends_factory(filter_backends, filterset_class)
    create_view = get_create_view_func('test', viewset, 'test')

    view = create_view('/test/', 'GET')
    operation = view.schema.get_operation('/test/', 'GET')

    assert operation['parameters'] == expected_parameters


def test_schema_for_viewset_with_filter_backend_strict_schema(
    settings, get_create_view_func, viewset_with_filter_backends_factory
):
    settings.API_STRICT_SCHEMA_VALIDATION = True
    viewset = viewset_with_filter_backends_factory([DjangoFilterBackend], FilterSetWithLabels)
    create_view = get_create_view_func('test', viewset, 'test')
    view = create_view('/test/', 'GET')

    view.schema.get_operation('/test/', 'GET')


def test_schema_for_viewset_with_filter_backend_strict_schema_raises(
    settings, get_create_view_func, viewset_with_filter_backends_factory
):
    settings.API_STRICT_SCHEMA_VALIDATION = True
    viewset = viewset_with_filter_backends_factory([DjangoFilterBackend], FilterSetWithNoLabels)
    create_view = get_create_view_func('test', viewset, 'test')
    view = create_view('/test/', 'GET')

    with pytest.raises(ImproperlyConfigured):
        view.schema.get_operation('/test/', 'GET')


@pytest.mark.parametrize('ignore,is_expected_allow', ((True, False), (False, True)))
def test_schema_for_viewset_allows_filters(ignore, is_expected_allow, settings, mocker):
    mocker.patch(
        'restdoctor.rest_framework.schema.openapi.RestDoctorSchema.view', return_value=None
    )
    mocker.patch('rest_framework.schemas.utils.is_list_view', return_value=False)
    mocker.patch('rest_framework.schemas.openapi.AutoSchema.allows_filters', return_value=True)
    settings.API_IGNORE_FILTER_PARAMS_FOR_DETAIL = ignore

    is_allow = RestDoctorSchema().allows_filters('path', 'method')

    assert is_allow is is_expected_allow

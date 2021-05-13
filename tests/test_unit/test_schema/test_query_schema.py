import pytest
from django.core.exceptions import ImproperlyConfigured
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from tests.test_unit.test_schema.stubs import (
    ListViewSetWithRequestSerializer,
    ListViewSetWithoutRequestSerializer,
    DefaultFilterSet,
    FilterSetWithNoLabels,
    FilterSetWithLabels,
)


@pytest.mark.parametrize(
    'viewset,expected_parameters',
    (
        (
            ListViewSetWithRequestSerializer,
            [
                {
                    'in': 'query',
                    'name': 'filter_uuid_field',
                    'required': False,
                    'schema': {
                        'type': 'string',
                        'format': 'uuid',
                    },
                },
                {
                    'in': 'query',
                    'name': 'filter_field',
                    'required': True,
                    'schema': {
                        'type': 'string',
                        'nullable': True,
                        'description': 'Help text',
                    },
                },
            ],
        ),
        (ListViewSetWithoutRequestSerializer, []),
    ),
)
def test_schema_for_list_viewset(get_create_view_func, viewset, expected_parameters):
    create_view = get_create_view_func('test', viewset, 'test')

    view = create_view('/test/', 'GET')
    operation = view.schema.get_operation('/test/', 'GET')

    assert operation['parameters'] == expected_parameters


@pytest.mark.parametrize(
    'viewset,expected_parameters',
    (
        (
            ListViewSetWithRequestSerializer,
            [
                {
                    'in': 'query',
                    'name': 'filter_uuid_field',
                    'required': False,
                    'schema': {
                        'type': 'string',
                        'format': 'uuid',
                    },
                },
                {
                    'in': 'query',
                    'name': 'filter_field',
                    'required': True,
                    'schema': {
                        'type': 'string',
                        'nullable': True,
                        'description': 'Help text',
                    },
                },
            ],
        ),
        (ListViewSetWithoutRequestSerializer, []),
    ),
)
def test_get_request_serializer_filter_parameters(
    get_create_view_func, viewset, expected_parameters
):
    list_view = get_create_view_func('test', viewset, 'test')

    view = list_view('/test/', 'GET')
    parameters = view.schema.get_request_serializer_filter_parameters('/test/', 'GET')

    assert parameters == expected_parameters


@pytest.mark.parametrize(
    'filter_backends,filterset_class,expected_parameters',
    (
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
                    'schema': {'type': 'string'},
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
                    'schema': {'type': 'string'},
                },
                {
                    'description': 'Event timestamp',
                    'in': 'query',
                    'name': 'my_model__timestamp__in',
                    'required': False,
                    'schema': {'type': 'string'},
                },
                {
                    'description': 'my another one model',
                    'in': 'query',
                    'name': 'my_another_one_model__isnull',
                    'required': False,
                    'schema': {'type': 'string'},
                },
                {
                    'description': 'Another One Event timestamp',
                    'in': 'query',
                    'name': 'my_another_one_model__timestamp',
                    'required': False,
                    'schema': {'type': 'string'},
                },
                {
                    'description': 'Another Event timestamp',
                    'in': 'query',
                    'name': 'created_at_date',
                    'required': False,
                    'schema': {'type': 'string'},
                },
                {
                    'description': 'created_after',
                    'in': 'query',
                    'name': 'created_after',
                    'required': False,
                    'schema': {'type': 'string'},
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
                    'schema': {'type': 'string'},
                },
                {
                    'description': 'Another One Event timestamp',
                    'in': 'query',
                    'name': 'my_another_one_model__timestamp',
                    'required': False,
                    'schema': {'type': 'string'},
                },
                {
                    'description': 'Created At Timestamp Label',
                    'in': 'query',
                    'name': 'created_at_date',
                    'required': False,
                    'schema': {'type': 'string'},
                },
                {
                    'description': 'Custom Method Label',
                    'in': 'query',
                    'name': 'created_after',
                    'required': False,
                    'schema': {'type': 'string'},
                },
            ],
        ),
    ),
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
    settings,
    get_create_view_func,
    viewset_with_filter_backends_factory,
):
    settings.API_STRICT_SCHEMA_VALIDATION = True
    viewset = viewset_with_filter_backends_factory([DjangoFilterBackend], FilterSetWithLabels)
    create_view = get_create_view_func('test', viewset, 'test')
    view = create_view('/test/', 'GET')

    view.schema.get_operation('/test/', 'GET')


def test_schema_for_viewset_with_filter_backend_strict_schema_raises(
    settings,
    get_create_view_func,
    viewset_with_filter_backends_factory,
):
    settings.API_STRICT_SCHEMA_VALIDATION = True
    viewset = viewset_with_filter_backends_factory([DjangoFilterBackend], FilterSetWithNoLabels)
    create_view = get_create_view_func('test', viewset, 'test')
    view = create_view('/test/', 'GET')

    with pytest.raises(ImproperlyConfigured):
        view.schema.get_operation('/test/', 'GET')

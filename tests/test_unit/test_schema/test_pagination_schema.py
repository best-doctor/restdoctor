import pytest
from django.utils.translation import gettext_lazy as _

from restdoctor.constants import DEFAULT_MAX_PAGE_SIZE
from restdoctor.rest_framework.pagination import CursorUUIDPagination
from restdoctor.rest_framework.pagination.page_number import PageNumberPagination
from restdoctor.rest_framework.schema import RestDoctorSchema


@pytest.mark.parametrize(
    ('pagination_class', 'expected_schema'),
    [
        (
            PageNumberPagination,
            {
                'type': 'object',
                'properties': {
                    'page': {'type': 'integer', 'minimum': 1, 'description': _('Selected page')},
                    'per_page': {
                        'type': 'integer',
                        'maximum': DEFAULT_MAX_PAGE_SIZE,
                        'description': _('Page size'),
                    },
                    'total': {'type': 'integer', 'description': _('Total result size')},
                    'url': {'type': 'string', 'description': _('Current page URL')},
                    'last_url': {
                        'type': 'string',
                        'nullable': True,
                        'description': _('Last page URL'),
                    },
                    'next_url': {
                        'type': 'string',
                        'nullable': True,
                        'description': _('Next page URL'),
                    },
                    'prev_url': {
                        'type': 'string',
                        'nullable': True,
                        'description': _('Previous page URL'),
                    },
                },
                'required': ['page', 'per_page', 'url', 'next_url', 'prev_url', 'total'],
            },
        ),
        (
            CursorUUIDPagination,
            {
                'type': 'object',
                'properties': {
                    'per_page': {
                        'type': 'integer',
                        'maximum': DEFAULT_MAX_PAGE_SIZE,
                        'description': _('Page size'),
                    },
                    'has_next': {'type': 'boolean', 'description': _('Has result next page')},
                    'before': {
                        'type': 'string',
                        'format': 'uuid',
                        'nullable': True,
                        'description': _('Before UUID'),
                    },
                    'after': {
                        'type': 'string',
                        'format': 'uuid',
                        'nullable': True,
                        'description': _('After UUID'),
                    },
                    'total': {'type': 'integer', 'description': _('Total result size')},
                    'url': {'type': 'string', 'description': _('Current page URL')},
                    'after_url': {
                        'type': 'string',
                        'nullable': True,
                        'description': _('URL of page after cursor position'),
                    },
                    'before_url': {
                        'type': 'string',
                        'nullable': True,
                        'description': _('URL of page before cursor position'),
                    },
                },
                'required': ['per_page', 'has_next', 'url', 'after_url', 'before_url', 'total'],
            },
        ),
    ],
)
def test_pagination_schema(pagination_class, expected_schema):
    paginator = pagination_class(view_schema=RestDoctorSchema())
    base_schema = {'properties': {}}

    schema = paginator.get_paginated_response_schema(base_schema)

    assert schema['properties']['meta'] == expected_schema

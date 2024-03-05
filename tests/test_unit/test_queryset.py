from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

from restdoctor.rest_framework.generics import GenericAPIView


@pytest.mark.parametrize(
    ('ignore', 'is_get_queryset_called', 'is_filter_queryset_called'),
    [(True, True, False), (False, True, True)],
)
def test_get_queryset_for_object(
    ignore, is_get_queryset_called, is_filter_queryset_called, mocker, settings
):
    settings.API_IGNORE_FILTER_PARAMS_FOR_DETAIL = ignore
    get_queryset = mocker.patch('rest_framework.generics.GenericAPIView.get_queryset')
    filter_queryset = mocker.patch('rest_framework.generics.GenericAPIView.filter_queryset')

    GenericAPIView()._get_queryset_for_object()

    assert get_queryset.called is is_get_queryset_called
    assert filter_queryset.called is is_filter_queryset_called


def test_get_object_use_get_queryset_for_object_without_lookup_fields(mocker):
    mocker.patch('restdoctor.rest_framework.generics.GenericAPIView._check_lookup_configuration')
    get_queryset_for_object = mocker.patch(
        'restdoctor.rest_framework.generics.GenericAPIView._get_queryset_for_object'
    )
    check_object_permissions = mocker.patch(
        'restdoctor.rest_framework.generics.GenericAPIView.check_object_permissions'
    )
    view = GenericAPIView()
    view.kwargs = {view.lookup_field: 'test_value'}
    view.request = None

    view.get_object()

    assert get_queryset_for_object.called is True
    assert check_object_permissions.called is True


@pytest.mark.parametrize(
    ('lookup_fields', 'expected_db_queries'),
    [
        ({'test': r'test_input_value'}, 1),
        (
            {
                'test1': r'test_input_value',
                'test2': r'test_input_value',
                'test3': r'test_input_value',
            },
            3,
        ),
        ({'test1': r'invalid_regex', 'test2': r'test_input_value', 'test3': r'invalid_regex'}, 1),
    ],
)
def test_get_object_use_get_queryset_for_object_with_lookup_fields_not_found(
    lookup_fields, expected_db_queries, mocker
):
    mocker.patch('restdoctor.rest_framework.generics.GenericAPIView._check_lookup_configuration')
    queryset = MagicMock()
    queryset.get.side_effect = ObjectDoesNotExist
    get_queryset_for_object = mocker.patch(
        'restdoctor.rest_framework.generics.GenericAPIView._get_queryset_for_object',
        return_value=queryset,
    )
    check_object_permissions = mocker.patch(
        'restdoctor.rest_framework.generics.GenericAPIView.check_object_permissions'
    )
    view = GenericAPIView()
    view.lookup_fields = lookup_fields
    view.lookup_url_kwarg = 'test_url_kwarg'
    view.kwargs = {view.lookup_url_kwarg: 'test_input_value'}

    with pytest.raises(Http404):
        view.get_object()

    assert get_queryset_for_object.called is True
    assert queryset.get.call_count == expected_db_queries
    assert check_object_permissions.called is False


@pytest.mark.parametrize(
    'lookup_fields',
    [
        {'test': r'test_input_value'},
        {'test1': r'test_input_value', 'test2': r'test_input_value', 'test3': r'test_input_value'},
        {'test1': r'invalid_regex', 'test2': r'test_input_value', 'test3': r'invalid_regex'},
    ],
)
def test_get_object_use_get_queryset_for_object_with_lookup_fields(lookup_fields, mocker):
    mocker.patch('restdoctor.rest_framework.generics.GenericAPIView._check_lookup_configuration')
    queryset = MagicMock()
    get_queryset_for_object = mocker.patch(
        'restdoctor.rest_framework.generics.GenericAPIView._get_queryset_for_object',
        return_value=queryset,
    )
    check_object_permissions = mocker.patch(
        'restdoctor.rest_framework.generics.GenericAPIView.check_object_permissions'
    )
    view = GenericAPIView()
    view.lookup_fields = lookup_fields
    view.lookup_url_kwarg = 'test_url_kwarg'
    view.kwargs = {view.lookup_url_kwarg: 'test_input_value'}
    view.request = None

    view.get_object()

    assert get_queryset_for_object.called is True
    assert queryset.get.call_count == 1
    assert check_object_permissions.called is True

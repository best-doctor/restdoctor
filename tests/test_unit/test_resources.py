from __future__ import annotations

import datetime

import pytest
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.test import RequestFactory
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_405_METHOD_NOT_ALLOWED

from restdoctor.rest_framework.resources import (
    ResourceView,
    ResourceViewSet,
    get_queryset_model_map,
)
from tests.test_unit.stubs import (
    ComplexResourceViewSet,
    ModelA,
    ModelAView,
    ModelAViewSet,
    ModelAWithMixinViewSet,
    ModelBViewSet,
    NoneViewSet,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('resource_views_map', 'expected_model_map'),
    [
        ({'one': ModelAViewSet}, {'one': ModelA}),
        ({'one': ModelAWithMixinViewSet}, {'one': ModelA}),
        ({'one': NoneViewSet}, {'one': None}),
    ],
)
def test_get_queryset_model_map_success_case(resource_views_map, expected_model_map):
    model_map = get_queryset_model_map(resource_views_map)

    assert model_map == expected_model_map


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('base_class', 'resource_views_map'),
    [
        (ResourceViewSet, {'one': ModelAViewSet}),
        (ResourceViewSet, {'one': ModelAViewSet, 'another': ModelAWithMixinViewSet}),
        (ResourceViewSet, {'one': ModelAViewSet, 'another': NoneViewSet}),
        (ResourceViewSet, {'one': NoneViewSet}),
        (ResourceView, {'one': ModelAViewSet}),
        (ResourceView, {'one': ModelAViewSet, 'another': ModelAWithMixinViewSet}),
        (ResourceView, {'one': ModelAViewSet, 'another': NoneViewSet}),
        (ResourceView, {'one': NoneViewSet}),
    ],
)
def test_check_queryset_models_success_case(base_class, resource_views_map):
    resource_class = type(
        'TestResourceViewSet', (base_class,), {'resource_views_map': resource_views_map}
    )

    result = resource_class.check_queryset_models()

    assert result is True


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('base_class', 'resource_views_map'),
    [
        (ResourceViewSet, {'one': ModelAViewSet, 'another': ModelBViewSet}),
        (ResourceView, {'one': ModelAViewSet, 'another': ModelBViewSet}),
    ],
)
def test_check_queryset_models_fail_case(base_class, resource_views_map):
    resource_class = type('TestResource', (base_class,), {'resource_views_map': resource_views_map})

    with pytest.raises(ImproperlyConfigured):
        resource_class.check_queryset_models()


@pytest.mark.django_db
def test_resource_viewset_dispatch_no_default_discriminator_fail_case(resource_viewset_dispatch):
    resource_discriminator = 'one'
    view_func, _ = resource_viewset_dispatch(
        resource_discriminator, ModelAViewSet, actions={'get': 'retrieve'}
    )
    request = RequestFactory().get('/')

    response = view_func(request)

    assert response.status_code == HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_resource_viewset_dispatch_wrong_discriminator_fail_case(resource_viewset_dispatch):
    resource_discriminator = 'one'
    view_func, _ = resource_viewset_dispatch(
        resource_discriminator, ModelAViewSet, actions={'get': 'retrieve'}
    )
    request = RequestFactory().get('/', {'view_type': f'NOT_{resource_discriminator}'})

    response = view_func(request)

    assert response.status_code == HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_resource_viewset_dispatch_success_case(resource_viewset_dispatch):
    resource_discriminator = 'one'
    view_func, mocked_dispatch = resource_viewset_dispatch(
        resource_discriminator, ModelAViewSet, actions={'get': 'retrieve'}
    )
    request = RequestFactory().get('/', {'view_type': resource_discriminator})

    view_func(request)

    assert mocked_dispatch.called_once()


@pytest.mark.django_db
def test_resource_view_dispatch_no_default_discriminator_fail_case(resource_view_dispatch):
    resource_discriminator = 'one'
    view_func, _ = resource_view_dispatch(resource_discriminator, ModelAView)
    request = RequestFactory().get('/')

    with pytest.raises(Http404):
        view_func(request)


@pytest.mark.django_db
def test_resource_view_dispatch_wrong_discriminator_fail_case(resource_view_dispatch):
    resource_discriminator = 'one'
    view_func, _ = resource_view_dispatch(resource_discriminator, ModelAView)
    request = RequestFactory().get('/', {'view_type': f'NOT_{resource_discriminator}'})

    with pytest.raises(Http404):
        view_func(request)


@pytest.mark.django_db
def test_resource_view_dispatch_success_case(resource_view_dispatch):
    resource_discriminator = 'one'
    view_func, mocked_dispatch = resource_view_dispatch(resource_discriminator, ModelAView)
    request = RequestFactory().get('/', {'view_type': resource_discriminator})

    view_func(request)

    assert mocked_dispatch.called_once()


@pytest.mark.parametrize(
    ('accept', 'view_type', 'expected_discriminant'),
    [
        ('application/vnd.vendor.v1', '', 'common'),
        ('application/vnd.vendor.v1', 'extended', 'extended'),
        ('application/vnd.vendor.v1-extended', '', 'extended'),
        ('application/vnd.vendor.v1-extended', 'common', 'extended'),
        ('application/vnd.vendor.v2', '', 'common'),
    ],
)
@pytest.mark.django_db
def test_get_discriminant_for_get_method(
    accept, view_type, expected_discriminant, settings, client, api_prefix, get_discriminant_spy
):
    settings.API_VERSIONS = {'v1': 'tests.stubs.api.v1_urls'}
    settings.API_RESOURCE_DEFAULT = 'common'

    client.get(f'/{api_prefix}mymodel/', HTTP_ACCEPT=accept, data={'view_type': view_type})

    assert get_discriminant_spy.spy_return == expected_discriminant


@pytest.mark.parametrize(
    ('accept', 'expected_discriminant'),
    [
        ('application/vnd.vendor.v1', 'common'),
        ('application/vnd.vendor.v1-common', 'common'),
        ('application/vnd.vendor.v1-extended', 'extended'),
    ],
)
@pytest.mark.django_db
def test_get_discriminant_for_post_method(
    accept, expected_discriminant, settings, client, api_prefix, get_discriminant_spy
):
    settings.API_VERSIONS = {'v1': 'tests.stubs.api.v1_urls'}
    settings.API_RESOURCE_DEFAULT = 'common'

    client.post(f'/{api_prefix}mymodel/', HTTP_ACCEPT=accept)

    assert get_discriminant_spy.spy_return == expected_discriminant


@pytest.mark.parametrize(
    ('discriminator', 'expected_status_code'),
    [
        ('read_write', HTTP_200_OK),
        ('read_only', HTTP_405_METHOD_NOT_ALLOWED),
        ('default', HTTP_404_NOT_FOUND),
    ],
)
def test_resource_view_dispatch_complex_case_post(mocker, discriminator, expected_status_code):
    mocked_get_discriminant = mocker.patch.object(ComplexResourceViewSet, 'get_discriminant')
    mocked_get_discriminant.return_value = discriminator
    view_func = ComplexResourceViewSet.as_view(actions={'get': 'retrieve', 'post': 'update'})
    request = RequestFactory().post('/')

    response = view_func(request)

    assert response.status_code == expected_status_code


@pytest.mark.xfail(
    reason='ViewSet with different actions set issue', until=datetime.datetime(2021, 5, 31)
)
@pytest.mark.parametrize(
    ('discriminator', 'expected_status_code'),
    [('read_write', HTTP_200_OK), ('read_only', HTTP_200_OK), ('default', HTTP_404_NOT_FOUND)],
)
def test_resource_view_dispatch_complex_case_get(mocker, discriminator, expected_status_code):
    mocked_get_discriminant = mocker.patch.object(ComplexResourceViewSet, 'get_discriminant')
    mocked_get_discriminant.return_value = discriminator
    view_func = ComplexResourceViewSet.as_view(actions={'get': 'retrieve', 'post': 'update'})
    request = RequestFactory().get('/')

    response = view_func(request)

    assert response.status_code == expected_status_code

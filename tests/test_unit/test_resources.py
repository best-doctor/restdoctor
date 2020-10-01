import pytest
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404
from django.test import RequestFactory

from restdoctor.rest_framework.resources import (
    get_queryset_model_map, ResourceViewSet, ResourceView,
)
from tests.test_unit.stubs import (
    ModelA, ModelAViewSet, ModelAWithMixinViewSet, NoneViewSet, ModelBViewSet, ModelAView,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'resource_views_map,expected_model_map',
    (
        (
            {'one': ModelAViewSet},
            {'one': ModelA},
        ),
        (
            {'one': ModelAWithMixinViewSet},
            {'one': ModelA},
        ),
        (
            {'one': NoneViewSet},
            {'one': None},
        ),
    ),
)
def test_get_queryset_model_map_success_case(resource_views_map, expected_model_map):
    model_map = get_queryset_model_map(resource_views_map)

    assert model_map == expected_model_map


@pytest.mark.django_db
@pytest.mark.parametrize(
    'base_class,resource_views_map',
    (
        (ResourceViewSet, {'one': ModelAViewSet}),
        (ResourceViewSet, {'one': ModelAViewSet, 'another': ModelAWithMixinViewSet}),
        (ResourceViewSet, {'one': ModelAViewSet, 'another': NoneViewSet}),
        (ResourceViewSet, {'one': NoneViewSet}),
        (ResourceView, {'one': ModelAViewSet}),
        (ResourceView, {'one': ModelAViewSet, 'another': ModelAWithMixinViewSet}),
        (ResourceView, {'one': ModelAViewSet, 'another': NoneViewSet}),
        (ResourceView, {'one': NoneViewSet}),
    ),
)
def test_check_queryset_models_success_case(base_class, resource_views_map):
    resource_class = type(
        'TestResourceViewSet', (base_class,), {'resource_views_map': resource_views_map},
    )

    result = resource_class.check_queryset_models()

    assert result is True


@pytest.mark.django_db
@pytest.mark.parametrize(
    'base_class,resource_views_map',
    (
        (ResourceViewSet, {'one': ModelAViewSet, 'another': ModelBViewSet}),
        (ResourceView, {'one': ModelAViewSet, 'another': ModelBViewSet}),
    ),
)
def test_check_queryset_models_fail_case(base_class, resource_views_map):
    resource_class = type(
        'TestResource', (base_class,), {'resource_views_map': resource_views_map},
    )

    with pytest.raises(ImproperlyConfigured):
        resource_class.check_queryset_models()


@pytest.mark.django_db
def test_resource_viewset_dispatch_no_default_discriminator_fail_case(resource_viewset_dispatch):
    resource_discriminator = 'one'
    view_func, _ = resource_viewset_dispatch(
        resource_discriminator, ModelAViewSet, actions={'get': 'retrieve'})
    request = RequestFactory().get('/')

    with pytest.raises(Http404):
        view_func(request)


@pytest.mark.django_db
def test_resource_viewset_dispatch_wrong_discriminator_fail_case(resource_viewset_dispatch):
    resource_discriminator = 'one'
    view_func, _ = resource_viewset_dispatch(
        resource_discriminator, ModelAViewSet, actions={'get': 'retrieve'})
    request = RequestFactory().get('/', {'view_type': f'NOT_{resource_discriminator}'})

    with pytest.raises(Http404):
        view_func(request)


@pytest.mark.django_db
def test_resource_viewset_dispatch_success_case(resource_viewset_dispatch):
    resource_discriminator = 'one'
    view_func, mocked_dispatch = resource_viewset_dispatch(
        resource_discriminator, ModelAViewSet, actions={'get': 'retrieve'})
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

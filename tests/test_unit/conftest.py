import pytest

from pytest_factoryboy import register
from restdoctor.rest_framework.pagination import (
    PageNumberPagination, PageNumberUncountedPagination,
    CursorUUIDPagination, CursorUUIDUncountedPagination,
)
from restdoctor.rest_framework.resources import ResourceViewSet, ResourceView
from restdoctor.utils.api_prefix import get_api_path_prefixes
from tests.factories import MyModelFactory
from tests.stubs.models import MyModel


register(MyModelFactory)


@pytest.fixture()
def n_models(my_model_factory):
    def generate_n_models(n_models, **kwargs):
        return my_model_factory.create_batch(n_models, **kwargs)
    return generate_n_models


@pytest.fixture()
def my_models_queryset():
    return MyModel.objects.all()


@pytest.fixture()
def page_number_pagination():
    return PageNumberPagination()


@pytest.fixture()
def page_number_uncounted_pagination():
    return PageNumberUncountedPagination()


@pytest.fixture()
def cursor_uuid_pagination():
    return CursorUUIDPagination()


@pytest.fixture()
def cursor_uuid_uncounted_pagination():
    return CursorUUIDUncountedPagination()


@pytest.fixture()
def api_prefix() -> str:
    api_prefixes = get_api_path_prefixes()
    if api_prefixes:
        return api_prefixes[0]
    return ''


@pytest.fixture()
def resource_viewset_dispatch(mocker):
    def with_args(resource_discriminator, resource_viewset, actions=None):
        resource_class = type(
            'TestResource', (ResourceViewSet,),
            {'resource_views_map': {resource_discriminator: resource_viewset}},
        )
        mocked_dispatch = mocker.patch.object(resource_viewset, 'dispatch')
        view_func = resource_class.as_view(actions=actions)

        return view_func, mocked_dispatch

    return with_args


@pytest.fixture()
def resource_view_dispatch(mocker):
    def with_args(resource_discriminator, resource_view, actions=None):
        resource_class = type(
            'TestResource', (ResourceView,),
            {'resource_views_map': {resource_discriminator: resource_view}},
        )
        mocked_dispatch = mocker.patch.object(resource_view, 'dispatch')
        view_func = resource_class.as_view()

        return view_func, mocked_dispatch

    return with_args

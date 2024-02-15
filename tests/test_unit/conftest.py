from __future__ import annotations

import enum
from unittest.mock import Mock

import pytest
from django.db.models import TextChoices
from pytest_factoryboy import register

from restdoctor.rest_framework.pagination import (
    CursorUUIDPagination,
    CursorUUIDUncountedPagination,
    PageNumberPagination,
    PageNumberUncountedPagination,
)
from restdoctor.rest_framework.resources import ResourceBase, ResourceView, ResourceViewSet
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
def resource_class(settings):
    def with_args(resource_discriminator, resource, base=None):
        class Base(base or ResourceViewSet):
            default_discriminative_value = settings.API_RESOURCE_DEFAULT
            resource_discriminative_param = settings.API_RESOURCE_DISCRIMINATIVE_PARAM

        resource_class = type(
            'TestResource', (Base,), {'resource_views_map': {resource_discriminator: resource}}
        )
        return resource_class

    return with_args


@pytest.fixture()
def resource_viewset_dispatch(mocker, resource_class):
    def with_args(resource_discriminator, resource_viewset, actions=None):
        viewset_class = resource_class(
            resource_discriminator, resource_viewset, base=ResourceViewSet
        )
        mocked_dispatch = mocker.patch.object(resource_viewset, 'dispatch')
        view_func = viewset_class.as_view(actions=actions)

        return view_func, mocked_dispatch

    return with_args


@pytest.fixture()
def resource_view_dispatch(mocker, resource_class):
    def with_args(resource_discriminator, resource_view):
        view_class = resource_class(resource_discriminator, resource_view, base=ResourceView)
        mocked_dispatch = mocker.patch.object(resource_view, 'dispatch')
        mocked_dispatch.__annotations__ = {}
        view_func = view_class.as_view()

        return view_func, mocked_dispatch

    return with_args


@pytest.fixture()
def get_discriminant_spy(mocker):
    return mocker.spy(ResourceBase, 'get_discriminant')


class TestStringEnum(enum.Enum):
    TEST = 'test'


class TestIntEnum(enum.Enum):
    TEST = 1


class TestBoolEnum(enum.Enum):
    TEST = True


class TestComplexEnum(enum.Enum):
    TEST = type('Class', (), {})


class TestTextChoices(TextChoices):
    TEST = 'test', 'test'


@pytest.fixture()
def mock_for_module(mocker):
    def with_args(module_name: str, function_name: str, *args, **kwargs) -> Mock:
        return mocker.patch(f'{module_name}.{function_name}', *args, **kwargs)

    return with_args

import pytest
from django.urls import resolve
from rest_framework.routers import SimpleRouter

from restdoctor.rest_framework.schema import RefsSchemaGenerator


class UrlConf:
    urlpatterns = []


@pytest.fixture()
def get_create_view_func():
    def with_args(prefix, viewset, basename, router=None):
        router = router or SimpleRouter()
        generator = RefsSchemaGenerator()

        router.register(prefix, viewset, basename=basename)
        urlconf = UrlConf()
        urlconf.urlpatterns = router.urls

        def create_view(path, method):
            match = resolve(path, urlconf)
            view = generator.create_view(match.func, method, None)
            return view

        return create_view
    return with_args


@pytest.fixture()
def get_resource_ref():
    def with_attrs(name):
        return {'$ref': f'#/components/schemas/{name}'}
    return with_attrs


@pytest.fixture()
def resource_default_ref(get_resource_ref):
    return get_resource_ref('Default')


@pytest.fixture()
def resource_another_ref(get_resource_ref):
    return get_resource_ref('Another')


@pytest.fixture()
def get_object_schema():
    def with_attrs(schema):
        return {'type': 'object', 'properties': {'data': schema}}
    return with_attrs


@pytest.fixture()
def resource_default_schema(get_object_schema, resource_default_ref):
    return get_object_schema(resource_default_ref)


@pytest.fixture()
def resource_another_schema(get_object_schema, resource_another_ref):
    return get_object_schema(resource_another_ref)

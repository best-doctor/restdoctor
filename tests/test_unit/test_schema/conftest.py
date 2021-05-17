import pytest
from django.urls import resolve
from rest_framework.routers import SimpleRouter

from restdoctor.rest_framework.schema import RefsSchemaGenerator
from restdoctor.rest_framework.viewsets import ModelViewSet
from tests.stubs.models import MyAnotherModel
from tests.stubs.serializers import MyModelSerializer


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
    def with_attrs(name, suffix):
        return {'$ref': f'#/components/schemas/{name}{suffix}'}

    return with_attrs


@pytest.fixture()
def resource_default_ref(get_resource_ref):
    def with_attrs(suffix):
        return get_resource_ref('tests_Default', suffix)

    return with_attrs


@pytest.fixture()
def resource_another_ref(get_resource_ref):
    def with_attrs(suffix):
        return get_resource_ref('tests_Another', suffix)

    return with_attrs


@pytest.fixture()
def get_object_schema():
    def with_attrs(schema):
        return {'type': 'object', 'properties': {'data': schema}}

    return with_attrs


@pytest.fixture()
def resource_default_rq_schema(get_object_schema, resource_default_ref):
    return get_object_schema(resource_default_ref('RQ'))


@pytest.fixture()
def resource_default_wq_schema(get_object_schema, resource_default_ref):
    return get_object_schema(resource_default_ref('WQ'))


@pytest.fixture()
def resource_another_rq_schema(get_object_schema, resource_another_ref):
    return get_object_schema(resource_another_ref('RQ'))


@pytest.fixture()
def resource_another_wq_schema(get_object_schema, resource_another_ref):
    return get_object_schema(resource_another_ref('WQ'))


@pytest.fixture()
def viewset_with_filter_backends_factory():
    def viewset_with_filter_backend(backends, filterset, **kwargs):
        class ModelViewSetWithFilterBackend(ModelViewSet):
            pagination_class = None
            queryset = MyAnotherModel.objects.all()
            serializer_class = MyModelSerializer
            filter_backends = backends
            filterset_class = filterset

        return ModelViewSetWithFilterBackend

    return viewset_with_filter_backend

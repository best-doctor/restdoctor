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

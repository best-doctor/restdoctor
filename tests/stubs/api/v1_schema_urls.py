from __future__ import annotations

from django.urls import include, path

from restdoctor.rest_framework.routers import ResourceRouter
from restdoctor.utils.api_prefix import get_api_path_prefixes
from tests.stubs.views import MyModelResourceView, MyModelResourceViewSet

api_prefixes = get_api_path_prefixes()

router = ResourceRouter()
router.register('mymodel', MyModelResourceViewSet, basename='my-model')

api_urlpatterns = [path('mymodels/', MyModelResourceView.as_view()), *router.urls]

urlpatterns = []

for api_prefix in api_prefixes:
    prefix_urlpattern = path(api_prefix, include((api_urlpatterns, 'api')))
    urlpatterns.append(prefix_urlpattern)

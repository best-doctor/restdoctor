from __future__ import annotations

import typing

from django.urls import path, include

from restdoctor.rest_framework.routers import ResourceRouter
from restdoctor.utils.api_prefix import get_api_path_prefixes
from tests.stubs.views import EmptyView, MyModelResourceViewSet

if typing.TYPE_CHECKING:
    from restdoctor.django.custom_types import URLPatternList

api_prefixes = get_api_path_prefixes()

router = ResourceRouter()
router.register('mymodel', MyModelResourceViewSet, basename='my-model')

api_urlpatterns: URLPatternList = [
    path('', EmptyView.as_view(), name='empty_view'),
    path('empty_v1', EmptyView.as_view(), name='empty_view_with_version'),
    *router.urls,
]

urlpatterns: URLPatternList = []

for api_prefix in api_prefixes:
    prefix_urlpattern = path(api_prefix, include((api_urlpatterns, 'api')))
    urlpatterns.append(prefix_urlpattern)

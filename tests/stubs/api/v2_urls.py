from __future__ import annotations

import typing

from django.urls import path, include
from restdoctor.utils.api_prefix import get_api_path_prefixes
from tests.stubs.views import EmptyView

if typing.TYPE_CHECKING:
    from restdoctor.django.custom_types import URLPatternList

api_prefixes = get_api_path_prefixes()

api_urlpatterns: URLPatternList = [
    path('', EmptyView.as_view(), name='empty_view'),
    path('empty_v2', EmptyView.as_view(), name='empty_view_with_version'),
]

urlpatterns: URLPatternList = []

for api_prefix in api_prefixes:
    prefix_urlpattern = path(api_prefix, include((api_urlpatterns, 'api')))
    urlpatterns.append(prefix_urlpattern)

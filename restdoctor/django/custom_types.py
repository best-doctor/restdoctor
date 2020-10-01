from __future__ import annotations
import typing as t

from django.http import HttpRequest, HttpResponse
from django.urls.resolvers import URLPattern

URLPatternList = t.List[URLPattern]
DjangoHandler = t.Callable[[HttpRequest], HttpResponse]

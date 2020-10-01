from __future__ import annotations
import typing

from django.utils.functional import lazy
from rest_framework.reverse import reverse as drf_reverse
from rest_framework.utils.urls import replace_query_param

if typing.TYPE_CHECKING:
    from rest_framework.request import Request
    from restdoctor.utils.custom_types import GenericContext


def preserve_resource_params(url: str, request: Request) -> str:
    if not request:
        return url

    args = getattr(request, 'resource_args', {})
    for param, value in args.items():
        url = replace_query_param(url, param, value)

    return url


def reverse(
    viewname: str,
    args: typing.List[typing.Any] = None, kwargs: GenericContext = None, request: Request = None,
    **extra: typing.Any,
) -> str:
    url = drf_reverse(viewname, args=args, kwargs=kwargs, request=request, **extra)
    return preserve_resource_params(url, request)


reverse_lazy = lazy(reverse, str)

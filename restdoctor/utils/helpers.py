from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from rest_framework.response import Response


def unpacked_error_message(response: Response) -> str:
    return response.json()['errors'][0]['message']


def get_full_class_name(obj: typing.Any) -> str:
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + '.' + obj.__class__.__name__

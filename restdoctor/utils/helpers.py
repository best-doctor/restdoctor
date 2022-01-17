from __future__ import annotations

import typing

from restdoctor.rest_framework.test_client import DRFClientResponse


def unpacked_error_message(response: DRFClientResponse) -> str:
    return response.json()['errors'][0]['message']


def get_full_class_name(obj: typing.Any) -> str:
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + '.' + obj.__class__.__name__

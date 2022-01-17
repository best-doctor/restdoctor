from __future__ import annotations

import json
import typing
from typing import Any, List

from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED,
    HTTP_204_NO_CONTENT,
)
from rest_framework.test import APIClient


class JsonResponse(typing.Protocol):
    # It goes from django.test.client.Client.request()

    def json(self) -> typing.Any:
        ...


class DRFClientResponse(JsonResponse, Response):
    pass


class DRFClient(APIClient):
    def __init__(
        self,
        user: Any = None,
        authorization: str = '',
        accept: str = 'application/json',
        content_type: str = 'application/json',
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.user = user
        self.content_type = content_type
        self.accept = accept
        self.authorization = authorization

    def delete(self, *args: Any, **kwargs: Any) -> DRFClientResponse:
        return self._api_call('delete', *args, **kwargs)

    def get(self, *args: Any, **kwargs: Any) -> DRFClientResponse:
        return self._api_call('get', *args, **kwargs)

    def post(self, *args: Any, **kwargs: Any) -> DRFClientResponse:
        return self._api_call('post', *args, **kwargs)

    def put(self, *args: Any, **kwargs: Any) -> DRFClientResponse:
        return self._api_call('put', *args, **kwargs)

    def patch(self, *args: Any, **kwargs: Any) -> DRFClientResponse:
        return self._api_call('patch', *args, **kwargs)

    def delete_json(self, *args: Any, **kwargs: Any) -> Any:
        expected_status_codes = kwargs.pop(
            'expected_status_codes', [HTTP_200_OK, HTTP_202_ACCEPTED, HTTP_204_NO_CONTENT]
        )
        return self._json_api_call(
            'delete', *args, expected_status_codes=expected_status_codes, **kwargs
        )

    def get_json(self, *args: Any, **kwargs: Any) -> Any:
        expected_status_codes = kwargs.pop('expected_status_codes', [HTTP_200_OK])
        return self._json_api_call(
            'get', *args, expected_status_codes=expected_status_codes, **kwargs
        )

    def post_json(self, *args: Any, **kwargs: Any) -> Any:
        expected_status_codes = kwargs.pop('expected_status_codes', [HTTP_200_OK, HTTP_201_CREATED])
        return self._json_api_call(
            'post', *args, expected_status_codes=expected_status_codes, **kwargs
        )

    def put_json(self, *args: Any, **kwargs: Any) -> Any:
        expected_status_codes = kwargs.pop('expected_status_codes', [HTTP_200_OK])
        return self._json_api_call(
            'put', *args, expected_status_codes=expected_status_codes, **kwargs
        )

    def patch_json(self, *args: Any, **kwargs: Any) -> Any:
        expected_status_codes = kwargs.pop('expected_status_codes', [HTTP_200_OK])
        return self._json_api_call(
            'patch', *args, expected_status_codes=expected_status_codes, **kwargs
        )

    def _api_call(
        self, method: str, *args: Any, expected_status_codes: List[int] = None, **kwargs: Any
    ) -> DRFClientResponse:
        accept = kwargs.get('accept') or kwargs.get('HTTP_ACCEPT') or self.accept
        authorization = (
            kwargs.get('authorization') or kwargs.get('HTTP_AUTHORIZATION') or self.authorization
        )
        content_type = kwargs.pop('content_type', self.content_type)

        if 'json' in kwargs:
            kwargs['data'] = json.dumps(kwargs.pop('json'))

        kwargs['HTTP_ACCEPT'] = accept
        kwargs['HTTP_AUTHORIZATION'] = authorization

        method = getattr(super(), method)
        response = method(*args, **kwargs, content_type=content_type)

        if expected_status_codes and response.status_code not in expected_status_codes:
            raise AssertionError(f'Response status code not in {expected_status_codes}')

        return response

    def _json_api_call(self, method: str, *args: Any, **kwargs: Any) -> Any:
        response = self._api_call(method, *args, **kwargs)
        return response.json()

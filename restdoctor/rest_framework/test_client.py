from __future__ import annotations
from typing import Any, List

from rest_framework.test import APIClient


class DRFClient(APIClient):
    def __init__(  # noqa CFQ002
        self, user: Any = None, authorization: str = '', accept: str = 'application/json',
        content_type: str = 'application/json', *args: Any, **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.content_type = content_type
        self.accept = accept
        self.authorization = authorization

    def delete(self, *args: Any, **kwargs: Any) -> Any:
        return self._api_call('delete', kwargs.get('expected_status_codes', [204]), *args, **kwargs)

    def get(self, *args: Any, **kwargs: Any) -> Any:
        return self._api_call('get', kwargs.get('expected_status_codes', [200]), *args, **kwargs)

    def post(self, *args: Any, **kwargs: Any) -> Any:
        return self._api_call('post', kwargs.get('expected_status_codes', [201]), *args, **kwargs)

    def put(self, *args: Any, **kwargs: Any) -> Any:
        return self._api_call('put', kwargs.get('expected_status_codes', [200]), *args, **kwargs)

    def patch(self, *args: Any, **kwargs: Any) -> Any:
        return self._api_call('patch', kwargs.get('expected_status_codes', [200]), *args, **kwargs)

    def _api_call(
        self, method: str, expected_status_codes: List[int], *args: Any, **kwargs: Any,
    ) -> Any:
        accept = kwargs.get('accept') or kwargs.get('HTTP_ACCEPT') or self.accept
        authorization = kwargs.get('authorization') or kwargs.get('HTTP_AUTHORIZATION') or self.authorization
        content_type = kwargs.get('content_type') or self.content_type

        kwargs['HTTP_ACCEPT'] = accept
        kwargs['HTTP_AUTHORIZATION'] = authorization

        method = getattr(super(), method)
        response = method(*args, **kwargs, content_type=content_type)

        if response.status_code not in expected_status_codes:
            raise AssertionError(f'Response status code not in {expected_status_codes}')

        return response.json()

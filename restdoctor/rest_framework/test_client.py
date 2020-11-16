from __future__ import annotations
from typing import Any

from rest_framework.test import APIClient


class DRFClient(APIClient):
    def __init__(  # noqa CFQ002
        self, user: Any = None, authorization_header: str = '', http_accept: str = 'application/json',
        content_type: str = 'application/json', *args: Any, **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.content_type = content_type
        self.http_accept = http_accept
        self.authorization_header = authorization_header

    def delete(self, *args: Any, **kwargs: Any) -> Any:
        return self._api_call('delete', kwargs.get('expected_status_code', 204), *args, **kwargs)

    def logout(self) -> None:
        self.credentials()
        super().logout()

    def get(self, *args: Any, **kwargs: Any) -> Any:
        return self._api_call('get', kwargs.get('expected_status_code', 200), *args, **kwargs)

    def post(self, *args: Any, **kwargs: Any) -> Any:
        return self._api_call('post', kwargs.get('expected_status_code', 201), *args, **kwargs)

    def put(self, *args: Any, **kwargs: Any) -> Any:
        return self._api_call('put', kwargs.get('expected_status_code', 200), *args, **kwargs)

    def patch(self, *args: Any, **kwargs: Any) -> Any:
        return self._api_call('patch', kwargs.get('expected_status_code', 200), *args, **kwargs)

    def _api_call(
        self, method: str, expected_status_code: int, *args: Any, **kwargs: Any,
    ) -> Any:
        http_accept = kwargs.get('HTTP_ACCEPT') or self.http_accept
        http_authorization = kwargs.get('HTTP_AUTHORIZATION') or self.authorization_header
        content_type = kwargs.get('content_type') or self.content_type

        self._set_header('HTTP_ACCEPT', http_accept)
        self._set_header('HTTP_AUTHORIZATION', http_authorization)

        method = getattr(super(), method)
        response = method(*args, **kwargs, content_type=content_type)

        if response.status_code != expected_status_code:
            raise AssertionError(f'Response status code != {expected_status_code}')

        return response.json()

    def _set_header(self, header_name: str, header_value: str) -> None:
        self._credentials.update({header_name: header_value})

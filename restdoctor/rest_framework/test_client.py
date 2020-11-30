from __future__ import annotations
from typing import Any, List, TYPE_CHECKING

from rest_framework.test import APIClient

if TYPE_CHECKING:
    from rest_framework.response import Response


class DRFClient(APIClient):
    def __init__(  # noqa CFQ002
        self, user: Any = None, authorization: str = '', accept: str = 'application/json',
        content_type: str = 'application/json', *args: Any, **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.content_type = content_type
        self.accept = accept
        self.authorization = authorization

    def delete(self, *args: Any, **kwargs: Any) -> Response:
        return self._api_call('delete', *args, **kwargs)

    def get(self, *args: Any, **kwargs: Any) -> Response:
        return self._api_call('get', *args, **kwargs)

    def post(self, *args: Any, **kwargs: Any) -> Response:
        return self._api_call('post', *args, **kwargs)

    def put(self, *args: Any, **kwargs: Any) -> Response:
        return self._api_call('put', *args, **kwargs)

    def patch(self, *args: Any, **kwargs: Any) -> Response:
        return self._api_call('patch', *args, **kwargs)

    def delete_json(self, *args: Any, **kwargs: Any) -> Any:
        return self._json_api_call('delete', kwargs.pop('expected_status_codes', None), *args, **kwargs)

    def get_json(self, *args: Any, **kwargs: Any) -> Any:
        return self._json_api_call('get', kwargs.pop('expected_status_codes', None), *args, **kwargs)

    def post_json(self, *args: Any, **kwargs: Any) -> Any:
        return self._json_api_call('post', kwargs.pop('expected_status_codes', None), *args, **kwargs)

    def put_json(self, *args: Any, **kwargs: Any) -> Any:
        return self._json_api_call('put', kwargs.pop('expected_status_codes', None), *args, **kwargs)

    def patch_json(self, *args: Any, **kwargs: Any) -> Any:
        return self._json_api_call('patch', kwargs.pop('expected_status_codes', None), *args, **kwargs)

    def _api_call(
        self, method: str, *args: Any, **kwargs: Any,
    ) -> Response:
        accept = kwargs.get('accept') or kwargs.get('HTTP_ACCEPT') or self.accept
        authorization = kwargs.get('authorization') or kwargs.get('HTTP_AUTHORIZATION') or self.authorization
        content_type = kwargs.get('content_type') or self.content_type

        kwargs['HTTP_ACCEPT'] = accept
        kwargs['HTTP_AUTHORIZATION'] = authorization

        method = getattr(super(), method)
        response = method(*args, **kwargs, content_type=content_type)

        return response

    def _json_api_call(
        self, method: str, expected_status_codes: List[int], *args: Any, **kwargs: Any,
    ) -> Any:
        response = self._api_call(method, *args, **kwargs)

        if expected_status_codes and response.status_code not in expected_status_codes:
            raise AssertionError(f'Response status code not in {expected_status_codes}')

        return response.json()

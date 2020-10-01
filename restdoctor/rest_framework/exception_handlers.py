from __future__ import annotations
import typing

from django.core.exceptions import PermissionDenied
from django.http import Http404
from ratelimit.exceptions import Ratelimited
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import set_rollback

if typing.TYPE_CHECKING:
    from restdoctor.utils.custom_types import ImmutableContext, GenericContext


def _get_full_details(detail: typing.Any) -> typing.Union[typing.List, typing.Dict]:  # noqa: CCR001
    if isinstance(detail, list):
        return [_get_full_details(item) for item in detail]
    elif isinstance(detail, dict):
        for field, value in detail.items():
            details = _get_full_details(value)
            for item in details:
                if not isinstance(item, dict):
                    continue
                item['field'] = field
            return details
    return {
        'message': detail,
        'code': detail.code,
    }


def _get_errors_data(exc: exceptions.APIException) -> GenericContext:
    full_details = _get_full_details(exc.detail)
    errors_data = {'message': exc.default_detail}
    if isinstance(full_details, list):
        errors_data['errors'] = full_details
    elif isinstance(full_details, dict):
        errors_data['errors'] = [full_details]
    return errors_data


def _override_exception(exc: Exception) -> Exception:
    if isinstance(exc, Http404):
        exc = exceptions.NotFound(exc)
    elif isinstance(exc, Ratelimited):
        exc = exceptions.PermissionDenied(
            detail={
                'message': 'Вы превысили лимит попыток. Попробуйте позже или обратитесь в поддержку.',
            },
            code='too_many_requests',
        )
    elif isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()
    return exc


def exception_handler(exc: Exception, context: ImmutableContext) -> typing.Optional[Response]:
    exc = _override_exception(exc)

    if isinstance(exc, exceptions.APIException):
        response_data = _get_errors_data(exc)

        headers = {}
        if getattr(exc, 'auth_header', None):
            headers['WWW-Authenticate'] = exc.auth_header

        wait = getattr(exc, 'wait', None)
        if wait:
            headers['Retry-After'] = wait
            response_data['retry_after'] = wait

        set_rollback()
        return Response(
            response_data,
            status=exc.status_code,
            headers=headers,
        )

    return None

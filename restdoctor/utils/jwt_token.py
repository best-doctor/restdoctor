from __future__ import annotations

import datetime
import typing

from django.conf import settings
from django.contrib.auth import get_user_model
from jwt import decode as jwt_decode, encode as jwt_encode

if typing.TYPE_CHECKING:
    from django.http import HttpRequest
    from django.contrib.auth.models import User


def decode_token(token: str) -> typing.Mapping:
    return jwt_decode(
        token,
        settings.SECRET_KEY,
        settings.JWT_VERIFY,
        options={
            'verify_exp': settings.JWT_VERIFY_EXPIRATION,
        },
        leeway=settings.JWT_LEEWAY,
        audience=settings.JWT_AUDIENCE,
        issuer=settings.JWT_ISSUER,
        algorithms=[settings.JWT_ALGORITHM],
    )


def encode_token(payload: typing.Dict) -> bytes:
    return jwt_encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def get_username_from_request_token(request: HttpRequest) -> typing.Optional[str]:
    header_parts = request.META.get('HTTP_AUTHORIZATION', '').split()
    if len(header_parts) == 2:
        if header_parts[0] == 'Bearer':
            payload = decode_token(header_parts[-1])

            return payload.get(get_user_model().USERNAME_FIELD)


def get_payload(user: User) -> typing.Dict:
    username = user.get_username()

    if hasattr(username, 'pk'):
        username = username.pk

    payload = {
        user.USERNAME_FIELD: username,
        'exp': datetime.datetime.utcnow() + settings.JWT_EXPIRATION_WEB_DELTA,
    }

    return payload


def get_token(user: User) -> bytes:
    payload = get_payload(user)
    return encode_token(payload)

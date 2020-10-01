from __future__ import annotations

from rest_framework.exceptions import APIException
from rest_framework import status

from restdoctor.constants import HTTP_420_GO_TO_HELL


class BadRequest(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Есть ошибки в формировании запроса.'
    default_code = 'bad_request'


class BusinessLogicException(APIException):
    status_code = HTTP_420_GO_TO_HELL
    default_detail = 'Что-то пошло не так, обратитесь в поддержку.'
    default_code = 'business_logic_error'

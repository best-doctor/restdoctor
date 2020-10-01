from __future__ import annotations
import datetime
from typing import Optional, Union, Any

from django.db import models
from rest_framework import ISO_8601
from rest_framework.fields import DateTimeField as BaseDateTimeField
from rest_framework.relations import HyperlinkedIdentityField as BaseHyperlinkedIdentityField
from rest_framework.request import Request
from rest_framework.settings import api_settings

from restdoctor.rest_framework.reverse import preserve_resource_params


class DateTimeField(BaseDateTimeField):
    def to_representation(
        self, value: datetime.datetime,
    ) -> Union[Optional[str], datetime.datetime]:
        if not value:
            return None

        output_format = getattr(self, 'format', api_settings.DATETIME_FORMAT)

        if output_format is None or isinstance(value, str):
            return value

        value = self.enforce_timezone(value)

        if output_format.lower() == ISO_8601:
            value = value.isoformat(timespec='microseconds')
            return value
        return value.strftime(output_format)


class HyperlinkedIdentityField(BaseHyperlinkedIdentityField):
    def get_url(self, obj: models.Model, view_name: str, request: Request, *args: Any, **kwargs: Any) -> str:
        url = super().get_url(obj, view_name, request, *args, **kwargs)
        return preserve_resource_params(url, request)

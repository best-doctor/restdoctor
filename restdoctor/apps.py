from django.apps import AppConfig as BaseConfig
from django.conf import settings

from restdoctor.rest_framework.fields import DateTimeField
from restdoctor import app_settings


class AppConfig(BaseConfig):
    name = 'restdoctor'

    def ready(self) -> None:
        from django.db import models
        from rest_framework.serializers import ModelSerializer

        field_mapping = ModelSerializer.serializer_field_mapping
        field_mapping[models.DateTimeField] = DateTimeField

        for setting in dir(app_settings):
            if setting.isupper() and not hasattr(settings, setting):
                setattr(settings, setting, getattr(app_settings, setting))

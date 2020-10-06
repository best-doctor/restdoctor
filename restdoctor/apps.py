from django.apps import AppConfig as BaseConfig

from restdoctor.rest_framework.fields import DateTimeField


class AppConfig(BaseConfig):
    name = 'restdoctor'

    def ready(self) -> None:
        from django.db import models
        from rest_framework.serializers import ModelSerializer

        field_mapping = ModelSerializer.serializer_field_mapping
        field_mapping[models.DateTimeField] = DateTimeField

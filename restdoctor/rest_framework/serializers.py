from __future__ import annotations

from rest_framework.serializers import (
    ModelSerializer as BaseModelSerializer, Serializer as BaseSerializer,
)


class Serializer(BaseSerializer):
    pass


class ModelSerializer(BaseModelSerializer):
    pass

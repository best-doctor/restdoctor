from rest_framework.serializers import Serializer, BaseSerializer, ListSerializer

from restdoctor.rest_framework.serializers import ModelSerializer
from tests.stubs.models import MyModel


class BaseObjectSerializer(Serializer):
    data = BaseSerializer(required=False, allow_null=True)


class BaseListSerializer(Serializer):
    data = ListSerializer(
        required=False, allow_empty=True,
        child=BaseSerializer(required=False, allow_null=True),
    )


class MyModelSerializer(ModelSerializer):
    class Meta:
        model = MyModel
        fields = ['uuid']


class MyModelExtendedSerializer(ModelSerializer):
    class Meta:
        model = MyModel
        fields = ['uuid', 'id']

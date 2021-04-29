import typing
from typing import Optional

from rest_framework.fields import CharField, SerializerMethodField
from rest_framework.serializers import Serializer, BaseSerializer, ListSerializer

from restdoctor.rest_framework.schema import SchemaWrapper
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


class MyModelWithoutHelpTextsSerializer(ModelSerializer):
    class Meta:
        model = MyModel
        fields = ['timestamp', 'abstract_field']

    abstract_field = CharField()


class WithMethodFieldFirstCorrectSerializer(Serializer):
    data = SchemaWrapper(
        SerializerMethodField(help_text='Some data'), schema_type=CharField(allow_null=True)
    )

    def get_data(self) -> Optional[str]:
        return None


class WithMethodFieldSecondCorrectSerializer(Serializer):
    data = SchemaWrapper(
        SerializerMethodField(help_text='Some data'), schema_type=CharField
    )

    def get_data(self) -> str:
        return 'some_data'


class WithMethodFieldFirstIncorrectSerializer(Serializer):
    data = SchemaWrapper(
        SerializerMethodField(help_text='Some data'), schema_type=CharField
    )

    def get_data(self) -> typing.Optional[str]:
        return None


class WithMethodFieldSecondIncorrectSerializer(Serializer):
    data = SchemaWrapper(
        SerializerMethodField(help_text='Some data'), schema_type=CharField(allow_null=True)
    )

    def get_data(self) -> str:
        return 'some_data'

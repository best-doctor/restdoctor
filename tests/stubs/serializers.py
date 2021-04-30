import typing
from typing import Optional, List

from rest_framework.fields import CharField, ListField, MultipleChoiceField, SerializerMethodField
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
        SerializerMethodField(help_text='Some data'), schema_type=CharField(allow_null=True),
    )

    def get_data(self) -> Optional[str]:
        return None


class WithMethodFieldSecondCorrectSerializer(Serializer):
    data = SchemaWrapper(
        SerializerMethodField(help_text='Some data'), schema_type=CharField,
    )

    def get_data(self) -> str:
        return 'some_data'


class WithMethodFieldFirstIncorrectSerializer(Serializer):
    data = SchemaWrapper(
        SerializerMethodField(help_text='Some data'), schema_type=CharField,
    )

    def get_data(self) -> typing.Optional[str]:
        return None


class WithMethodFieldSecondIncorrectSerializer(Serializer):
    data = SchemaWrapper(
        SerializerMethodField(help_text='Some data'), schema_type=CharField(allow_null=True),
    )

    def get_data(self) -> str:
        return 'some_data'


class WithMethodFieldManyIncorrectSerializer(Serializer):
    data = SchemaWrapper(
        SerializerMethodField(help_text='Some data'), schema_type=Serializer(many=True),
    )

    def get_data(self) -> str:
        return ''


class WithMethodFieldOptionalManyIncorrectSerializer(Serializer):
    data = SchemaWrapper(
        SerializerMethodField(help_text='Some data'), schema_type=Serializer(allow_null=True),
    )

    def get_data(self) -> Optional[List]:
        return None


class WithMethodFieldManyCorrectSerializer(Serializer):
    data = SchemaWrapper(
        SerializerMethodField(help_text='Some data'), schema_type=Serializer(many=True),
    )

    def get_data(self) -> List[str]:
        return ['some_data']


class WithMethodFieldOptionalManyCorrectSerializer(Serializer):
    data = SchemaWrapper(
        SerializerMethodField(help_text='Some data'),
        schema_type=Serializer(many=True, allow_null=True),
    )

    def get_data(self) -> Optional[List]:
        return None


class WithMethodFieldListFieldCorrectSerializer(Serializer):
    data = SchemaWrapper(
        SerializerMethodField(help_text='Some data'),
        schema_type=ListField(child=CharField()),
    )

    def get_data(self) -> str:
        return ''


class WithMethodFieldListFieldIncorrectSerializer(Serializer):
    data = SchemaWrapper(
        SerializerMethodField(help_text='Some data'),
        schema_type=ListField(child=CharField()),
    )

    def get_data(self) -> List[str]:
        return ['some_data']


class WithMethodFieldMultipleChoiceFieldCorrectSerializer(Serializer):
    data = SchemaWrapper(
        SerializerMethodField(help_text='Some data'),
        schema_type=MultipleChoiceField(choices=[]),
    )

    def get_data(self) -> str:
        return ''


class WithMethodFieldMultipleChoiceFieldIncorrectSerializer(Serializer):
    data = SchemaWrapper(
        SerializerMethodField(help_text='Some data'),
        schema_type=MultipleChoiceField(choices=[]),
    )

    def get_data(self) -> List[str]:
        return ['some_data']

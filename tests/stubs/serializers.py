from __future__ import annotations

import typing
from typing import List, Optional

from rest_framework.fields import CharField, ListField, MultipleChoiceField, SerializerMethodField
from rest_framework.serializers import BaseSerializer, ListSerializer, Serializer

from restdoctor.rest_framework.schema import SchemaWrapper
from restdoctor.rest_framework.serializers import ModelSerializer
from tests.stubs.models import MyModel

if typing.TYPE_CHECKING:
    String = str


class BaseObjectSerializer(Serializer):
    data = BaseSerializer(required=False, allow_null=True)


class BaseListSerializer(Serializer):
    data = ListSerializer(
        required=False, allow_empty=True, child=BaseSerializer(required=False, allow_null=True)
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


class WithMethodFieldSerializer(Serializer):
    field = SchemaWrapper(SerializerMethodField(help_text='Some data'), schema_type=CharField)
    optional_field = SchemaWrapper(
        SerializerMethodField(help_text='Some data'), schema_type=CharField(allow_null=True)
    )
    many_field = SchemaWrapper(
        SerializerMethodField(help_text='Some data'), schema_type=Serializer(many=True)
    )
    list_field = SchemaWrapper(
        SerializerMethodField(help_text='Some data'), schema_type=ListField(child=CharField())
    )
    optional_many_field = SchemaWrapper(
        SerializerMethodField(help_text='Some data'),
        schema_type=Serializer(many=True, allow_null=True),
    )
    optional_list_field = SchemaWrapper(
        SerializerMethodField(help_text='Some data'),
        schema_type=ListField(child=CharField(), allow_null=True),
    )
    multiple_choice_field = SchemaWrapper(
        SerializerMethodField(help_text='Some data'), schema_type=MultipleChoiceField(choices=[])
    )
    type_checking_field = SchemaWrapper(
        SerializerMethodField(help_text='Some data'), schema_type=CharField
    )
    incorrect_field = SchemaWrapper(
        SerializerMethodField(help_text='Some data'), schema_type=CharField(allow_null=True)
    )
    incorrect_optional_field = SchemaWrapper(
        SerializerMethodField(help_text='Some data'), schema_type=CharField
    )
    incorrect_many_field = SchemaWrapper(
        SerializerMethodField(help_text='Some data'), schema_type=Serializer(many=True)
    )
    incorrect_list_field = SchemaWrapper(
        SerializerMethodField(help_text='Some data'), schema_type=ListField(child=CharField())
    )
    incorrect_optional_many_field = SchemaWrapper(
        SerializerMethodField(help_text='Some data'), schema_type=Serializer(allow_null=True)
    )
    incorrect_multiple_choice_field = SchemaWrapper(
        SerializerMethodField(help_text='Some data'), schema_type=MultipleChoiceField(choices=[])
    )

    def get_field(self) -> str:
        return 'some_data'

    def get_optional_field(self) -> Optional[str]:
        return None

    def get_many_field(self) -> List[str]:
        return ['some_data']

    def get_list_field(self) -> typing.List[str]:
        return ['some_data']

    def get_optional_many_field(self) -> Optional[List]:
        return None

    def get_optional_list_field(self) -> typing.Optional[typing.List]:
        return None

    def get_incorrect_optional_field(self) -> typing.Optional[str]:
        return None

    def get_incorrect_field(self) -> str:
        return 'some_data'

    def get_incorrect_many_field(self) -> str:
        return ''

    def get_incorrect_list_field(self) -> str:
        return ''

    def get_incorrect_optional_many_field(self) -> Optional[List]:
        return None

    def get_multiple_choice_field(self) -> List[str]:
        return ['some_data']

    def get_incorrect_multiple_choice_field(self) -> str:
        return ''

    def get_type_checking_field(self) -> String:
        return ''

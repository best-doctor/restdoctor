from rest_framework.fields import CharField
from restdoctor.rest_framework.serializers import ModelSerializer, Serializer
from tests.stubs.models import MyModel


class ParentModelSerializer(ModelSerializer):
    class Meta:
        model = MyModel
        fields = ['field_parent_1', 'field_parent_2']

    field_parent_1 = CharField()
    field_parent_2 = CharField()


class ParentSerializer(Serializer):
    class Meta:
        fields = ['field_parent_1', 'field_parent_2']

    field_parent_1 = CharField()
    field_parent_2 = CharField()


class SerializerMixinA(Serializer):
    class Meta:
        fields = ['field_mixin_a']

    field_mixin_a = CharField()
    field_mixin_a_not_in_meta = CharField()


class SerializerMixinB(Serializer):
    field_mixin_b = CharField()

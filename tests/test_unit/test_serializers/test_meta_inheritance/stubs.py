from rest_framework.fields import CharField
from restdoctor.rest_framework.serializers import ModelSerializer, Serializer
from restdoctor.rest_framework.viewsets import ListModelViewSet
from tests.stubs.models import MyModel
from tests.test_unit.stubs import SerializerA


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


class SerializerMeta(Serializer):
    char_field = CharField()


class ListViewSetWithMetaSerializer(ListModelViewSet):
    serializer_class_map = {'default': SerializerA, 'list': {'meta': SerializerMeta}}


class ListViewSetWithRequestSerializer(ListModelViewSet):
    serializer_class_map = {'default': SerializerA}


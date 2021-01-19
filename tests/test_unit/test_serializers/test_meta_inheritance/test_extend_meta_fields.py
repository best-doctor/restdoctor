import pytest
from rest_framework.fields import CharField

from restdoctor.rest_framework.serializers import extend_meta_fields

from tests.test_unit.test_serializers.test_meta_inheritance.stubs import (
    ParentModelSerializer, ParentSerializer, SerializerMixinA, SerializerMixinB,
)


@pytest.mark.parametrize(
    'parent_serializer_cls',
    [
        ParentSerializer,
        ParentModelSerializer,
    ],
)
def test_with_all_parents_explicit(parent_serializer_cls):
    class ChildSerializer(SerializerMixinA, SerializerMixinB, parent_serializer_cls):
        class Meta:
            fields = extend_meta_fields(
                SerializerMixinA, 'field_child_3', parent_serializer_cls, SerializerMixinB, 'field_child_1')

        field_child_1 = CharField()
        field_child_2 = CharField()
        field_child_3 = CharField()

    assert ChildSerializer.Meta.fields == [
        'field_mixin_a', 'field_child_3', 'field_parent_1', 'field_parent_2', 'field_mixin_b', 'field_child_1',
    ]


def test_with_all_parents_implicit():
    class ChildSerializer(SerializerMixinA, SerializerMixinB, ParentModelSerializer):
        class Meta:
            fields = extend_meta_fields('field_child_3', 'field_child_1')

        field_child_1 = CharField()
        field_child_2 = CharField()
        field_child_3 = CharField()

    assert ChildSerializer.Meta.fields == [
        'field_mixin_a', 'field_mixin_b', 'field_parent_1', 'field_parent_2', 'field_child_3', 'field_child_1',
    ]


def test_with_some_parents():
    class ChildSerializer(SerializerMixinA, SerializerMixinB, ParentModelSerializer):
        class Meta:
            fields = extend_meta_fields(SerializerMixinA, ParentModelSerializer, 'field_child')

        field_child = CharField()

    assert ChildSerializer.Meta.fields == ['field_mixin_a', 'field_parent_1', 'field_parent_2', 'field_child']


def test_without_extend():
    class ChildSerializer(SerializerMixinA, SerializerMixinB, ParentModelSerializer):
        class Meta:
            fields = ['field_child_3', 'field_child_1']

        field_child_1 = CharField()
        field_child_2 = CharField()
        field_child_3 = CharField()

    assert ChildSerializer.Meta.fields == ['field_child_3', 'field_child_1']

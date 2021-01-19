from tests.test_unit.test_serializers.test_meta_inheritance.stubs import (
    MyModel, ParentModelSerializer, SerializerMixinA, SerializerMixinB,
)


def test_no_meta_in_child():
    class ChildSerializer(ParentModelSerializer):
        pass

    assert 'Meta' not in ChildSerializer.__dict__


def test_no_meta_model_in_parents():
    class ChildSerializer(SerializerMixinA, SerializerMixinB):
        class Meta:
            pass

    assert not hasattr(ChildSerializer.Meta, 'model')


def test_inherited_from_parent():
    class ChildSerializer(SerializerMixinA, ParentModelSerializer, SerializerMixinB):
        class Meta:
            pass

    assert 'Meta' in ChildSerializer.__dict__
    assert ChildSerializer.Meta.__bases__ == (object,)
    assert ChildSerializer.Meta.model is MyModel


def test_inherited_from_grandparent():
    class SubSerializer(ParentModelSerializer):
        pass

    class ChildSerializer(SubSerializer):
        class Meta:
            pass

    assert 'Meta' in ChildSerializer.__dict__
    assert ChildSerializer.Meta.__bases__ == (object,)
    assert ChildSerializer.Meta.model is MyModel


def test_is_not_inherited_if_defined_in_child():
    class MyChildModel(MyModel):
        class Meta:
            app_label = 'bestdoctor'

    class ChildSerializer(ParentModelSerializer):
        class Meta:
            model = MyChildModel

    assert ChildSerializer.Meta.model is MyChildModel

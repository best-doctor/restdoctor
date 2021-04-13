from __future__ import annotations

from django.db import models
from rest_framework.fields import CharField, SerializerMethodField
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer, Serializer

from restdoctor.rest_framework.generics import GenericAPIView
from restdoctor.rest_framework.resources import ResourceViewSet
from restdoctor.rest_framework.schema import SchemaWrapper
from restdoctor.rest_framework.serializers import ModelSerializer
from restdoctor.rest_framework.views import RetrieveAPIView
from restdoctor.rest_framework.viewsets import ListModelViewSet, ModelViewSet, ReadOnlyModelViewSet


class ModelWithoutSensitiveData(models.Model):
    class Meta:
        app_label = 'restdoctor'

    title = models.CharField(max_length=100, blank=True)


class ChildSensitiveDataModel(models.Model):
    class Meta:
        app_label = 'restdoctor'

    class SensitiveData:
        include = ['title']

    title = models.CharField(max_length=100, blank=True)
    field_fk = models.ForeignKey(
        ModelWithoutSensitiveData, on_delete=models.PROTECT, blank=True, null=True
    )


class ParentSensitiveDataModel(models.Model):
    class Meta:
        app_label = 'restdoctor'

    class SensitiveData:
        include = ['title']

    title = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    field_fk = models.ForeignKey(
        ChildSensitiveDataModel, on_delete=models.PROTECT, blank=True, null=True
    )
    field_m2m = models.ManyToManyField(ChildSensitiveDataModel, blank=True)
    field_o2o = models.OneToOneField(
        ChildSensitiveDataModel, on_delete=models.PROTECT, blank=True, null=True
    )


class SerializerWithSensitiveData(Serializer):
    class SensitiveData:
        include = ['field1', 'field2']

    field1 = CharField()
    field2 = CharField()


class SerializerWithoutSensitiveData(Serializer):
    field1 = CharField()


class ModelSerializerWithSensitiveData(ModelSerializer):
    class Meta:
        model = ParentSensitiveDataModel
        fields = [
            'first_name',
            'last_name',
            'title',
            'field_fk',
            'field_m2m',
            'field_o2o',
            'field1',
            'field2',
            'field3',
        ]

    class SensitiveData:
        include = ['first_name', 'last_name']

    first_name = CharField()
    field1 = SerializerWithSensitiveData()
    field2 = SchemaWrapper(SerializerMethodField(), schema_type=SerializerWithSensitiveData)
    field3 = SerializerWithSensitiveData(many=True)


class PermissionA(BasePermission):
    pass


class PermissionB(BasePermission):
    pass


class PermissionC(BasePermission):
    pass


permission_classes_map_with_default = {'default': [PermissionA], 'retrieve': [PermissionB]}


permission_classes_map_no_default = {'retrieve': [PermissionB]}


class ModelA(models.Model):
    class Meta:
        app_label = 'restdoctor'


class ModelB(models.Model):
    class Meta:
        app_label = 'restdoctor'


class ModelAMixin:
    queryset = ModelA.objects.none()


class ModelBMixin:
    queryset = ModelB.objects.none()


class ModelAViewSet(ModelViewSet):
    queryset = ModelA.objects.none()


class ModelAView(RetrieveAPIView):
    queryset = ModelA.objects.none()


class ModelAWithMixinViewSet(ModelAMixin, ModelViewSet):
    pass


class ModelBViewSet(ModelViewSet):
    queryset = ModelB.objects.none()


class ModelBWithMixinViewSet(ModelBMixin, ModelViewSet):
    pass


class NoneViewSet(ModelViewSet):
    pass


class SerializerA(BaseSerializer):
    pass


class SerializerB(BaseSerializer):
    pass


class ListViewSetWithRequestSerializer(ListModelViewSet):
    serializer_class_map = {'default': SerializerA, 'list': {'request': SerializerB}}


class ListViewSetWithoutRequestSerializer(ListModelViewSet):
    serializer_class_map = {'default': SerializerA}


class ROViewSet(ReadOnlyModelViewSet):
    serializer_class_map = {'default': SerializerA}

    def dispatch(self, *args, **kwargs):
        return super(GenericAPIView, self).dispatch(*args, **kwargs)

    def retrieve(self, *args, **kwargs):
        return Response({})


class RWViewSet(ModelViewSet):
    serializer_class_map = {'default': SerializerA}

    def dispatch(self, *args, **kwargs):
        return super(GenericAPIView, self).dispatch(*args, **kwargs)

    def retrieve(self, *args, **kwargs):
        return Response({})

    def update(self, *args, **kwargs):
        return Response({})


class ComplexResourceViewSet(ResourceViewSet):
    resource_views_map = {'read_only': ROViewSet, 'read_write': RWViewSet}

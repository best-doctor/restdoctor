from __future__ import annotations

from django.db.models import QuerySet
from django_filters import CharFilter, DateFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework.decorators import action as drf_action
from rest_framework.fields import CharField, UUIDField
from rest_framework.serializers import Serializer

from restdoctor.rest_framework.resources import ResourceViewSet
from restdoctor.rest_framework.views import SerializerClassMapApiView
from restdoctor.rest_framework.viewsets import ListModelViewSet, ModelViewSet, ReadOnlyModelViewSet
from tests.stubs.models import MyAnotherModel


class DefaultSerializer(Serializer):
    default_field = CharField()


class AnotherSerializer(Serializer):
    another_field = CharField()


class CreateSerializer(Serializer):
    create_field = CharField()


class ListSerializer(Serializer):
    list_field = CharField()


class SomeFieldSerializer(Serializer):
    some_field = CharField(help_text='serializer some field')


class ListFilterSerialiser(Serializer):
    filter_uuid_field = UUIDField(required=False)
    filter_field = CharField(allow_null=True, help_text='Help text')


class SerializerClassMapViewSet(ModelViewSet):
    serializer_class_map = {
        'default': DefaultSerializer,
        'list': {'response': ListSerializer},
        'create': {'response': CreateSerializer},
    }


class SerializerClassMapView(SerializerClassMapApiView):
    serializer_class_map = {
        'default': DefaultSerializer,
        'get': {'response': ListSerializer},
        'post': {'response': CreateSerializer},
    }

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass


class DefaultViewSet(ModelViewSet):
    serializer_class = DefaultSerializer


class AnotherViewSet(ModelViewSet):
    serializer_class = AnotherSerializer


class ROModelViewSet(ReadOnlyModelViewSet):
    serializer_class = DefaultSerializer


class DefaultViewSetWithOperationId(DefaultViewSet):
    schema_operation_id_map = {
        'list': 'listDefaultBars',
        'retrieve': 'getDefaultBar',
        'create': 'createDefaultBar',
        'update': 'updateDefaultBar',
        'partial_update': 'partialUpdateDefaultBar',
        'destroy': 'deleteDefaultBar',
    }


class ActionsViewSet(ModelViewSet):
    serializer_class = DefaultSerializer

    schema_action_codes_map = {'custom_action': {'200': None, '201': 'Description for 201 code.'}}

    @drf_action(detail=True, methods=['put'])
    def custom_action(self, *args, **kwargs):
        return {}


class ViewSetWithTags(ModelViewSet):
    schema_tags = ['tag1', 'tag2']
    serializer_class = DefaultSerializer


class ListViewSetWithRequestSerializer(ListModelViewSet):
    pagination_class = None
    schema_tags = ['tag']
    serializer_class_map = {'default': DefaultSerializer, 'list': {'request': ListFilterSerialiser}}


class ListViewSetWithoutRequestSerializer(ListModelViewSet):
    pagination_class = None
    serializer_class_map = {'default': DefaultSerializer}


class DefaultAnotherResourceViewSet(ResourceViewSet):
    default_discriminative_value = 'default'
    resource_views_map = {
        'default': DefaultViewSet,
        'another': AnotherViewSet,
        'read_only': ROModelViewSet,
        'actions': ActionsViewSet,
    }


class SingleResourceViewSet(ResourceViewSet):
    default_discriminative_value = 'default'
    resource_views_map = {'another': AnotherViewSet}


class SomeFieldFilterSet(FilterSet):
    some_field = CharFilter(label='filter some field')


class MultipleSiblingParametersView(ReadOnlyModelViewSet):
    serializer_class_map = {'default': DefaultSerializer, 'list': {'request': SomeFieldSerializer}}
    filter_backends = [DjangoFilterBackend]
    filterset_class = SomeFieldFilterSet

    def get(self, request, *args, **kwargs):
        pass


class DefaultFilterSet(FilterSet):
    class Meta:
        model = MyAnotherModel
        fields = ['uuid', 'timestamp']


class FilterSetWithNoLabels(FilterSet):
    class Meta:
        model = MyAnotherModel
        fields = {
            'uuid': ['exact'],
            'my_model__timestamp': ['exact', 'in'],
            'my_another_one_model': ['isnull'],
            'my_another_one_model__timestamp': ['exact'],
        }

    created_at_date = DateFilter(field_name='timestamp', lookup_expr='date__exact')
    created_after = DateFilter(method='filter_created_after')

    @staticmethod
    def filter_created_after(queryset: QuerySet, name: str, value: str) -> QuerySet:
        return queryset.filter(timestamp__gte=value)


class FilterSetWithLabels(FilterSet):
    class Meta:
        model = MyAnotherModel
        fields = ['uuid', 'my_model__timestamp', 'my_another_one_model__timestamp']

    created_at_date = DateFilter(
        label='Created At Timestamp Label', field_name='timestamp', lookup_expr='date__exact'
    )
    created_after = DateFilter(label='Custom Method Label', method='filter_created_after')

    @staticmethod
    def filter_created_after(queryset: QuerySet, name: str, value: str) -> QuerySet:
        return queryset.filter(timestamp__gte=value)

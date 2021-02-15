from rest_framework.decorators import action as drf_action
from rest_framework.fields import CharField, UUIDField
from rest_framework.serializers import Serializer

from restdoctor.rest_framework.resources import ResourceViewSet
from restdoctor.rest_framework.views import SerializerClassMapApiView
from restdoctor.rest_framework.viewsets import ModelViewSet, ListModelViewSet


class DefaultSerializer(Serializer):
    default_field = CharField()


class AnotherSerializer(Serializer):
    another_field = CharField()


class CreateSerializer(Serializer):
    create_field = CharField()


class ListSerializer(Serializer):
    list_field = CharField()


class ListFilterSerialiser(Serializer):
    filter_uuid_field = UUIDField(required=False)
    filter_field = CharField(allow_null=True, help_text='Help text')


class SerializerClassMapViewSet(ModelViewSet):
    serializer_class_map = {
        'default': DefaultSerializer,
        'list': {
            'response': ListSerializer,
        },
        'create': {
            'response': CreateSerializer,
        },
    }


class SerializerClassMapView(SerializerClassMapApiView):
    serializer_class_map = {
        'default': DefaultSerializer,
        'get': {
            'response': ListSerializer,
        },
        'post': {
            'response': CreateSerializer,
        },
    }

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass


class DefaultViewSet(ModelViewSet):
    serializer_class = DefaultSerializer


class AnotherViewSet(ModelViewSet):
    serializer_class = AnotherSerializer


class ActionsViewSet(ModelViewSet):
    serializer_class = DefaultSerializer

    schema_action_codes_map = {
        'custom_action': {
            '200': None,
            '201': 'Description for 201 code.',
        },
    }

    @drf_action(detail=True, methods=['put'])
    def custom_action(self, *args, **kwargs):
        return {}


class ViewSetWithTags(ModelViewSet):
    schema_tags = ['tag1', 'tag2']
    serializer_class = DefaultSerializer


class ListViewSetWithRequestSerializer(ListModelViewSet):
    pagination_class = None
    schema_tags = ['tag']
    serializer_class_map = {
        'default': DefaultSerializer,
        'list': {
            'request': ListFilterSerialiser,
        }
    }


class ListViewSetWithoutRequestSerializer(ListModelViewSet):
    pagination_class = None
    serializer_class_map = {
        'default': DefaultSerializer,
    }


class DefaultAnotherResourceViewSet(ResourceViewSet):
    default_discriminative_value = 'default'
    resource_views_map = {
        'default': DefaultViewSet,
        'another': AnotherViewSet,
        'actions': ActionsViewSet,
    }

from rest_framework.serializers import Serializer, BaseSerializer, ListSerializer


class BaseObjectSerializer(Serializer):
    data = BaseSerializer(required=False, allow_null=True)


class BaseListSerializer(Serializer):
    data = ListSerializer(
        required=False, allow_empty=True,
        child=BaseSerializer(required=False, allow_null=True),
    )

from __future__ import annotations

from rest_framework.serializers import BaseSerializer


class SerializerA(BaseSerializer):
    pass


class SerializerB(BaseSerializer):
    pass


class SerializerC(BaseSerializer):
    pass


class SerializerD(BaseSerializer):
    pass


class SerializerE(BaseSerializer):
    pass


class SerializerF(BaseSerializer):
    pass


class SerializerG(BaseSerializer):
    pass


serializer_class_map_with_default = {
    'default': SerializerA,
    'retrieve': {'request': SerializerB},
    'list': {'request': SerializerB, 'response': SerializerB},
    'create': {'request': SerializerC, 'response': SerializerB},
}

serializer_class_map_no_default = {
    'retrieve': {'request': SerializerB},
    'list': {'request': SerializerB, 'response': SerializerB},
    'create': {'request': SerializerC, 'response': SerializerB},
}


serializer_class_map_with_format = {
    'default': SerializerA,
    'default.compact': SerializerB,
    'default.version:2': SerializerG,
    'retrieve': {'response': SerializerB, 'response.compact': SerializerC},
    'list': {
        'response.full': SerializerE,
        'response.version:12': SerializerF,
        'response.test:name': SerializerG,
    },
}

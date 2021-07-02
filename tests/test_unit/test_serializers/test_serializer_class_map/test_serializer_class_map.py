from __future__ import annotations

import pytest

from restdoctor.utils.serializers import get_serializer_class_from_map
from tests.test_unit.test_serializers.test_serializer_class_map.stubs import (
    SerializerA,
    SerializerB,
    SerializerC,
    SerializerD,
    SerializerE,
    SerializerF,
    SerializerG,
    serializer_class_map_no_default,
    serializer_class_map_with_default,
    serializer_class_map_with_format,
)


@pytest.mark.parametrize(
    'serializer_class_map,action,stage,default,expected',
    (
        (serializer_class_map_with_default, 'retrieve', 'request', SerializerD, SerializerB),
        (serializer_class_map_with_default, 'retrieve', 'response', SerializerD, SerializerA),
        (serializer_class_map_with_default, 'list', 'response', SerializerD, SerializerB),
        (serializer_class_map_no_default, 'retrieve', 'request', SerializerD, SerializerB),
        (serializer_class_map_no_default, 'retrieve', 'response', SerializerD, SerializerD),
        (serializer_class_map_no_default, 'list', 'response', SerializerD, SerializerB),
    ),
)
def test_get_serializer_class_from_map(serializer_class_map, action, stage, default, expected):
    serializer_class = get_serializer_class_from_map(action, stage, serializer_class_map, default)

    assert serializer_class == expected


@pytest.mark.parametrize(
    'serializer_class_map,action,stage,api_format,default,expected',
    (
        (serializer_class_map_with_format, 'retrieve', 'request', None, SerializerD, SerializerB),
        (serializer_class_map_with_format, 'retrieve', 'response', None, SerializerD, SerializerC),
        (
            serializer_class_map_with_format,
            'retrieve',
            'response',
            'full',
            SerializerD,
            SerializerB,
        ),
        (
            serializer_class_map_with_format,
            'list',
            'response',
            'with_related',
            SerializerD,
            SerializerA,
        ),
        (
            serializer_class_map_with_format,
            'create',
            'response',
            'version:12',
            SerializerD,
            SerializerG,
        ),
        (
            serializer_class_map_with_format,
            'create',
            'response',
            'version:1',
            SerializerD,
            SerializerA,
        ),
        (serializer_class_map_with_format, 'list', 'request', None, SerializerD, SerializerB),
        (serializer_class_map_with_format, 'list', 'response', 'full', SerializerD, SerializerE),
        (
            serializer_class_map_with_format,
            'list',
            'response',
            'version:2',
            SerializerD,
            SerializerG,
        ),
        (
            serializer_class_map_with_format,
            'list',
            'response',
            'version:12',
            SerializerD,
            SerializerF,
        ),
        (
            serializer_class_map_with_format,
            'list',
            'response',
            'version:15',
            SerializerD,
            SerializerF,
        ),
        (
            serializer_class_map_with_format,
            'list',
            'response',
            'version:33',
            SerializerD,
            SerializerF,
        ),
        (
            serializer_class_map_with_format,
            'list',
            'response',
            'test:name',
            SerializerD,
            SerializerG,
        ),
    ),
)
def test_get_serializer_class_from_map_with_format(
    serializer_class_map, action, stage, api_format, default, expected, settings
):
    settings.API_DEFAULT_FORMAT = 'compact'
    settings.API_FORMATS = ('full', 'compact', 'version:{2,12,33,15}', 'test:name')

    serializer_class = get_serializer_class_from_map(
        action, stage, serializer_class_map, default, api_format=api_format
    )

    assert serializer_class == expected

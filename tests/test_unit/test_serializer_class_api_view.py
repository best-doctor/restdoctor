import pytest

from tests.test_unit.stubs import (
    ListViewSetWithRequestSerializer, SerializerB, ListViewSetWithoutRequestSerializer,
    SerializerA,
)


@pytest.mark.parametrize(
    'viewset,use_default,expected',
    (
            (ListViewSetWithRequestSerializer, True, SerializerB),
            (ListViewSetWithRequestSerializer, False, SerializerB),
            (ListViewSetWithoutRequestSerializer, True, SerializerA),
            (ListViewSetWithoutRequestSerializer, False, None),
    ),
)
def test_get_request_serializer_class(viewset, use_default, expected):
    list_view = viewset(request=None, action='list')

    request_serializer_class = list_view.get_request_serializer_class(use_default=use_default)

    assert request_serializer_class == expected


@pytest.mark.parametrize(
    'viewset,use_default,expected',
    (
            (ListViewSetWithRequestSerializer, True, SerializerB),
            (ListViewSetWithRequestSerializer, False, SerializerB),
            (ListViewSetWithoutRequestSerializer, True, SerializerA),
    ),
)
def test_get_request_serializer(viewset, use_default, expected):
    list_view = viewset(request=None, action='list', format_kwarg=None)

    request_serializer = list_view.get_request_serializer(use_default=use_default)

    assert isinstance(request_serializer, expected)


def test_get_request_serializer_none():
    list_view = ListViewSetWithoutRequestSerializer(request=None, action='list', format_kwarg=None)

    request_serializer = list_view.get_request_serializer(use_default=False)

    assert request_serializer is None

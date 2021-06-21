import pytest

from tests.test_unit.test_serializers.test_meta_inheritance.stubs import (
    ListViewSetWithMetaSerializer,
    ListViewSetWithRequestSerializer,
)


@pytest.mark.parametrize(
    'viewset,meta_data,result',
    (
            (ListViewSetWithMetaSerializer, {'char_field': 'test'}, {'char_field': 'test'}),
            (ListViewSetWithMetaSerializer, {'char_field': 'test', 'data': {}}, {'char_field': 'test'}),
            (ListViewSetWithMetaSerializer, {'char_field': 'test', 'data': []}, {'char_field': 'test'}),
            (ListViewSetWithRequestSerializer, {'char_field': 'test'}, {}),
            (ListViewSetWithRequestSerializer, {'char_field': 'test', 'data': []}, {}),
            (ListViewSetWithRequestSerializer, {'char_field': 'test', 'data': {}}, {}),
            (ListViewSetWithRequestSerializer, {}, {}),
    ),
)
def test_meta_data_serializer_success(mocker, viewset, meta_data, result):
    list_view = viewset(request=None, action='list', format_kwarg=None)
    mocker_meta_data = mocker.patch.object(list_view, 'get_meta_data')
    mocker_meta_data.return_value = meta_data

    assert list_view.get_meta_serializer_data() == result


@pytest.mark.parametrize(
    'meta_data,error_class',
    (
            ({'data': {}}, KeyError),
            ({'data': 'test'}, KeyError),
            ({'data': None}, KeyError),
            ({'data': []}, KeyError),
            ({}, KeyError),
            ([], AttributeError),
            ([{'char_field': 'test'}], AttributeError),
    ),
)
def test_meta_data_serializer_error(mocker, meta_data, error_class):
    list_view = ListViewSetWithMetaSerializer(request=None, action='list', format_kwarg=None)
    mocker_meta_data = mocker.patch.object(list_view, 'get_meta_data')
    mocker_meta_data.return_value = meta_data

    with pytest.raises(error_class):
        list_view.get_meta_serializer_data()

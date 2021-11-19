import pytest

from restdoctor.rest_framework.generics import GenericAPIView


@pytest.mark.parametrize(
    'ignore,is_get_queryset_called,is_filter_queryset_called',
    ((True, True, False), (False, True, True)),
)
def test_get_queryset_for_object(
    ignore, is_get_queryset_called, is_filter_queryset_called, mocker, settings
):
    settings.API_IGNORE_FILTER_PARAMS_FOR_DETAIL = ignore
    get_queryset = mocker.patch('rest_framework.generics.GenericAPIView.get_queryset')
    filter_queryset = mocker.patch('rest_framework.generics.GenericAPIView.filter_queryset')

    GenericAPIView()._get_queryset_for_object()

    assert get_queryset.called is is_get_queryset_called
    assert filter_queryset.called is is_filter_queryset_called


@pytest.mark.parametrize('lookup_fields', (None, {'test': 'test'}))
def test_get_object_use_get_queryset_for_object(lookup_fields, mocker):
    mocker.patch('restdoctor.rest_framework.generics.GenericAPIView._check_lookup_configuration')
    get_queryset_for_object = mocker.patch(
        'restdoctor.rest_framework.generics.GenericAPIView._get_queryset_for_object'
    )
    view = GenericAPIView()
    view.lookup_fields = lookup_fields

    try:
        view.get_object()
    except AttributeError:
        pass

    assert get_queryset_for_object.called

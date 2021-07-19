from __future__ import annotations

import pytest
from django.test import RequestFactory

from tests.test_unit.stubs import ModelAViewSet


@pytest.mark.django_db
def test_retrieve_get_item_success_case(mocker, resource_viewset_dispatch):
    resource_discriminator = 'one'
    mocker_get_item = mocker.patch.object(ModelAViewSet, 'get_item')
    view_func, mocked_dispatch = resource_viewset_dispatch(
        resource_discriminator, ModelAViewSet, actions={'get': 'retrieve'}
    )
    request = RequestFactory().get('/', {'view_type': resource_discriminator})

    view_func(request)

    assert mocker_get_item.called_once()
    assert mocked_dispatch.called_once()

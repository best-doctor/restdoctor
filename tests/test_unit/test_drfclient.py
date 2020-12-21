import pytest

from restdoctor.rest_framework.test_client import DRFClient


@pytest.fixture()
def drf_client():
    return DRFClient()


@pytest.mark.parametrize(
    'method',
    [
        'delete',
        'get',
        'patch',
        'post',
        'put',
    ]
)
def test_call_api_with_content_type(drf_client, method):
    drf_client._api_call(method, path='test/path', content_type='another_type')


@pytest.mark.parametrize(
    'method',
    [
        'delete',
        'get',
        'patch',
        'post',
        'put',
    ]
)
def test_call_api(drf_client, method):
    drf_client._api_call(method, path='test/path')

import pytest

from restdoctor.rest_framework.test_client import DRFClient


@pytest.fixture()
def drf_client():
    return DRFClient()


@pytest.fixture()
def mock_api_call_factory(mocker):
    def mock_api_call(method):
        return mocker.patch('restdoctor.rest_framework.test_client.APIClient.' + method)
    return mock_api_call

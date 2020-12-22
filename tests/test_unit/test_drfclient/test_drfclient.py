import pytest


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
def test_call_api(method, drf_client, mock_api_call_factory):
    api_call = mock_api_call_factory(method)
    called_method = getattr(drf_client, method)

    called_method('test/path')

    api_call.assert_called_once_with(
        'test/path', HTTP_ACCEPT='application/json', HTTP_AUTHORIZATION='', content_type='application/json')


@pytest.mark.parametrize(
    ('method', 'content_type'),
    [
        ('delete', 'application/json'),
        ('get', 'multipart'),
        ('patch', 'multipart'),
        ('post', 'multipart'),
        ('put', 'multipart'),
    ]
)
def test_call_api_with_content_type(method, content_type, drf_client, mock_api_call_factory):
    api_call = mock_api_call_factory(method)
    called_method = getattr(drf_client, method)

    called_method('test/path', content_type=content_type)

    api_call.assert_called_once_with(
        'test/path', HTTP_ACCEPT='application/json', HTTP_AUTHORIZATION='', content_type=content_type)

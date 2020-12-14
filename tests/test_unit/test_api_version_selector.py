import pytest


@pytest.mark.parametrize(
    'endpoint, accept, expected_content_type',
    [
        (
            'empty_v1',
            'application/vnd.restdoctor',
            'application/vnd.restdoctor.v1.full+json',
        ),
        (
            'empty_v1',
            'application/vnd.restdoctor.v1',
            'application/vnd.restdoctor.v1.full+json',
        ),
        (
            'empty_v1',
            'application/vnd.restdoctor.v1.compact',
            'application/vnd.restdoctor.v1.compact+json',
        ),
        (
            'empty_v1',
            'application/vnd.restdoctor.v1.compact-verbose',
            'application/vnd.restdoctor.v1.compact-verbose+json',
        ),
        (
            'empty_v2',
            'application/vnd.restdoctor.v2',
            'application/vnd.restdoctor.v2.full+json',
        ),
        (
            'empty_v2',
            'application/vnd.restdoctor.v2.compact',
            'application/vnd.restdoctor.v2.compact+json',
        ),
        (
            'empty_v2',
            'application/vnd.restdoctor.v2.compact-verbose',
            'application/vnd.restdoctor.v2.compact-verbose+json',
        ),
        (
            'empty_v2',
            'application/vnd.restdoctor.v2.wrong-format',
            'application/vnd.restdoctor.v2.full+json',
        ),
    ],
)
@pytest.mark.django_db
def test_accept_header_version_success_case(
    client, api_prefix, endpoint, accept, expected_content_type, settings,
):
    settings.API_VERSIONS = {
        'v1': 'tests.stubs.api.v1_urls',
        'v2': 'tests.stubs.api.v2_urls',
    }
    settings.API_FORMATS = ('full', 'compact', 'compact-verbose')
    settings.API_VENDOR_STRING = 'RestDoctor'

    response = client.get(f'/{api_prefix}{endpoint}', HTTP_ACCEPT=accept)

    assert response.status_code == 200
    assert response['Content-Type'] == expected_content_type


@pytest.mark.parametrize(
    'endpoint, accept',
    [
        (
            'empty_v1',
            'application/json',
        ),
    ],
)
@pytest.mark.django_db
def test_accept_header_fallback_success_case(client, api_prefix, endpoint, accept, settings):
    settings.API_VERSIONS = {
        'v1': 'tests.stubs.api.v1_urls',
        'v2': 'tests.stubs.api.v2_urls',
    }

    response = client.get(f'/{api_prefix}{endpoint}', HTTP_ACCEPT=accept)

    assert response.status_code == 404


@pytest.mark.parametrize(
    'endpoint, content_type',
    [
        (
            'empty_v1',
            'application/vnd.restdoctor.v1.full+json',
        ),
    ],
)
@pytest.mark.django_db
def test_post_without_accept_header_success_case(client, api_prefix, endpoint, content_type, settings):
    settings.API_VERSIONS = {
        'v1': 'tests.stubs.api.v1_urls',
        'v2': 'tests.stubs.api.v2_urls',
    }
    settings.API_VENDOR_STRING = 'RestDoctor'

    response = client.post(
        f'/{api_prefix}{endpoint}', data='{}',
        content_type='application/json', HTTP_ACCEPT='application/vnd.restdoctor',
    )

    assert response.status_code == 200
    assert response['Content-Type'] == content_type

import pytest

from restdoctor.utils.media_type import parse_accept


def test_parse_none():
    result = parse_accept(None)

    assert result is None


@pytest.mark.parametrize(
    'header,expected_version',
    (
        ('*/*', 'fallback'),
        ('text/html', 'fallback'),
        ('application/json', 'fallback'),
        ('application/vnd.bestdoctor', 'default'),
    ),
)
def test_parse_accept_fallback(settings, header, expected_version):
    settings.API_FALLBACK_VERSION = 'fallback'
    settings.API_DEFAULT_VERSION = 'default'
    settings.API_VERSIONS = {
        'v1': 'v1',
        'v2': 'v2',
    }
    settings.API_FALLBACK_FOR_APPLICATION_JSON_ONLY = False

    result = parse_accept(header)

    assert expected_version == result.version


@pytest.mark.parametrize(
    'header,expected_version',
    (
        ('*/*', 'default'),
        ('text/html', 'default'),
        ('application/json', 'fallback'),
        ('application/vnd.bestdoctor', 'default'),
    ),
)
def test_parse_accept_default(settings, header, expected_version):
    settings.API_FALLBACK_VERSION = 'fallback'
    settings.API_DEFAULT_VERSION = 'default'
    settings.API_VERSIONS = {
        'v1': 'v1',
        'v2': 'v2',
    }
    settings.API_FALLBACK_FOR_APPLICATION_JSON_ONLY = True

    result = parse_accept(header)

    assert expected_version == result.version


@pytest.mark.parametrize(
    'header,expected_version',
    (
        ('application/vnd.bestdoctor', 'default'),
        ('application/vnd.bestdoctor.v1', 'v1'),
        ('application/vnd.bestdoctor.v1.full', 'v1'),
        ('application/vnd.bestdoctor.v1.full+json', 'v1'),
        ('application/vnd.bestdoctor.v2', 'v2'),
        ('application/vnd.bestdoctor.v2.full', 'v2'),
        ('application/vnd.bestdoctor.v2.full+json', 'v2'),
        ('application/vnd.bestdoctor.v3', 'default'),
        ('application/vnd.bestdoctor.v3.full', 'default'),
        ('application/vnd.bestdoctor.v3.full+json', 'default'),
    ),
)
def test_parse_accept_versions(settings, header, expected_version):
    settings.API_FALLBACK_VERSION = 'fallback'
    settings.API_DEFAULT_VERSION = 'default'
    settings.API_VERSIONS = {
        'v1': 'v1',
        'v2': 'v2',
    }

    result = parse_accept(header)

    assert expected_version == result.version


@pytest.mark.parametrize(
    'vendor,expected_vendor',
    (
        (None, 'vendor'),
        ('', 'vendor'),
        ('my_vendor', 'my_vendor'),
    ),
)
def test_parse_accept_vendor_success_case(vendor, expected_vendor):
    result = parse_accept('application/vnd', vendor=vendor)

    assert expected_vendor == result.vendor

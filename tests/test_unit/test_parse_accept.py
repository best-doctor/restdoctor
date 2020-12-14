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
        ('application/vnd.vendor', 'default'),
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
        ('application/vnd.vendor', 'default'),
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
    ('header', 'expected_version', 'expected_discriminator'),
    [
        ('application/vnd.vendor', 'default', None),
        ('application/vnd.vendor.v1', 'v1', None),
        ('application/vnd.vendor.v1.full', 'v1', None),
        ('application/vnd.vendor.v1.full+json', 'v1', None),
        ('application/vnd.vendor.v1-extended', 'v1', 'extended'),
        ('application/vnd.vendor.v1-extended.full', 'v1', 'extended'),
        ('application/vnd.vendor.v1-extended.full+json', 'v1', 'extended'),
        ('application/vnd.vendor.v2', 'v2', None),
        ('application/vnd.vendor.v2.full', 'v2', None),
        ('application/vnd.vendor.v2.full+json', 'v2', None),
        ('application/vnd.vendor.v2-extended', 'v2', 'extended'),
        ('application/vnd.vendor.v2-extended.full', 'v2', 'extended'),
        ('application/vnd.vendor.v2-extended.full+json', 'v2', 'extended'),
        ('application/vnd.vendor.v3', 'default', None),
        ('application/vnd.vendor.v3.full', 'default', None),
        ('application/vnd.vendor.v3.full+json', 'default', None),
        ('application/vnd.vendor.v3-extended', 'default', 'extended'),
        ('application/vnd.vendor.v3-extended.full', 'default', 'extended'),
        ('application/vnd.vendor.v3-extended.full+json', 'default', 'extended'),
    ],
)
def test_parse_accept_versions_and_resource_discriminator(settings, header, expected_version, expected_discriminator):
    settings.API_FALLBACK_VERSION = 'fallback'
    settings.API_DEFAULT_VERSION = 'default'
    settings.API_RESOURCE_DEFAULT = 'common'
    settings.API_VERSIONS = {
        'v1': 'v1',
        'v2': 'v2',
    }

    result = parse_accept(header)

    assert expected_version == result.version
    assert expected_discriminator == result.resource_discriminator


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

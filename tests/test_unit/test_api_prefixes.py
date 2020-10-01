import pytest

from restdoctor.utils.api_prefix import get_api_prefixes, get_api_path_prefixes


@pytest.mark.parametrize(
    'api_prefixes,default,expected_result',
    (
        ('/prefix', None, ('/prefix',)),
        (('/prefix',), None, ('/prefix',)),
        (None, None, ()),
        (None, '/prefix', ('/prefix',)),
        (('/prefix1', '/prefix2'), None, ('/prefix1', '/prefix2')),
    ),
)
def test_get_api_prefixes_success_case(api_prefixes, default, expected_result, settings):
    settings.API_PREFIXES = api_prefixes
    result = get_api_prefixes(default=default)

    assert result == expected_result


@pytest.mark.parametrize(
    'api_prefixes,default,expected_result',
    (
        ('/prefix', None, ('prefix/',)),
        (('/prefix',), None, ('prefix/',)),
        (None, None, ()),
        (None, '/prefix', ('prefix/',)),
        (('/prefix1', '/prefix2'), None, ('prefix1/', 'prefix2/')),
    ),
)
def test_get_api_path_prefixes_success_case(api_prefixes, default, expected_result, settings):
    settings.API_PREFIXES = api_prefixes
    result = get_api_path_prefixes(default=default)

    assert result == expected_result

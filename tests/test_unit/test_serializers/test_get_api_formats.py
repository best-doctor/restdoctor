from __future__ import annotations

import pytest

from restdoctor.utils.serializers import get_api_formats


@pytest.mark.parametrize(
    'formats,default,expected',
    (
        (('full', 'compact'), 'compact', ['compact']),
        (('full', 'compact'), 'full', ['full']),
        (('full', 'compact:{3,2,1}'), 'compact:2', ['compact:1', 'compact:2']),
        (('full', 'compact:{3,2,1}'), 'full', ['full']),
        (('full', 'test:32'), 'full', ['full']),
        (('full', 'test:{32}'), 'test:32', ['test:32']),
        (('full', 'my_name:1'), 'my_name:1', ['my_name:1']),
        (('full', 'my_name:{32}'), 'my_name:32', ['my_name:32']),
        (('full', 'my_name:{32,433,14}'), 'my_name:32', ['my_name:14', 'my_name:32']),
    ),
)
def test_get_api_formats(settings, formats, default, expected):
    settings.API_FORMATS = formats
    api_formats = get_api_formats(default)

    assert api_formats == expected

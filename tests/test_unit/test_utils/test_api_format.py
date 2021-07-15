from __future__ import annotations

import pytest

from restdoctor.utils.api_format import get_available_format, get_filter_formats


@pytest.mark.parametrize(
    'formats,api_format,expected',
    (
        (('full', 'compact', 'big'), 'compact', ['compact']),
        (('full', 'compact'), 'full', ['full']),
        (('full', 'compact:{3,2,1}'), 'compact:2', ['compact:1', 'compact:2']),
        (('full', 'compact:{3,2,1}'), 'full', ['full']),
        (('full', 'test:32'), 'full', ['full']),
        (('full', 'test:{32}'), 'test:32', ['test:32']),
        (('full', 'my_name:1', 'mobile:1:2'), 'my_name:1', ['my_name:1']),
        (('full', 'mobile:1:2'), 'mobile:1:2', ['mobile:1:2']),
        (('full', 'my_name:{32}'), 'my_name:32', ['my_name:32']),
        (
            ('full', 'my_name:{1,2}', 'my_name:{15,12,30}'),
            'my_name:15',
            ['my_name:12', 'my_name:15'],
        ),
        (('full', 'my_name:{32,433,14}'), 'my_name:32', ['my_name:14', 'my_name:32']),
    ),
)
def test_get_filter_formats(formats, api_format, expected):
    api_formats = get_filter_formats(formats, api_format)

    assert api_formats == expected


@pytest.mark.parametrize(
    'formats,expected',
    (
        (('full', 'compact'), ['full', 'compact']),
        (('full', 'compact:{3,2,1}'), ['full', 'compact:1', 'compact:2', 'compact:3']),
        (('full', 'test:32'), ['full', 'test:32']),
        (('full', 'test:{32}'), ['full', 'test:32']),
        (('full', 'my_name:1'), ['full', 'my_name:1']),
        (('full', 'mobile:1:2'), ['full', 'mobile:1:2']),
        (('full', 'mobile:'), ['full', 'mobile:']),
        (('full', 'my_name:3!2'), ['full', 'my_name:3!2']),
        (('test', 'my_name:{32,433,14}'), ['test', 'my_name:14', 'my_name:32', 'my_name:433']),
    ),
)
def test_get_available_format(formats, expected):
    api_formats = get_available_format(formats)

    assert api_formats == expected

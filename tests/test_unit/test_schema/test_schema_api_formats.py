from __future__ import annotations

import pytest

from restdoctor.rest_framework.schema import RefsSchemaGenerator


@pytest.mark.parametrize(
    ('api_format', 'expected_api_format'),
    [
        (('full', 'compact', 'compact-verbose'), ['full', 'compact', 'compact-verbose']),
        (('full', 'compact:{12,32}'), ['full', 'compact:12', 'compact:32']),
        (('compact:{12}',), ['compact:12']),
        (('test:{1,2,3,4}',), ['test:1', 'test:2', 'test:3', 'test:4']),
        (('full', 'compact:12'), ['full', 'compact:12']),
    ],
)
def test_schema_with_tags_success_case(settings, api_format, expected_api_format):
    settings.API_FORMATS = api_format

    refs_schema = RefsSchemaGenerator()

    assert refs_schema.api_formats == expected_api_format

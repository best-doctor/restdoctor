from __future__ import annotations

import pytest
from rest_framework.fields import Field, FileField

from restdoctor.rest_framework.schema.generators import (
    RefsSchemaGenerator,
    RefsSchemaGenerator30,
    RefsSchemaGenerator31,
)
from tests.test_unit.test_schema.stubs import DefaultViewSet


@pytest.mark.parametrize(
    ('field', 'expected_schema'),
    [
        (Field(allow_null=True), {'type': ['string', 'null']}),
        (FileField(), {'type': 'string', 'contentMediaType': 'application/octet-stream'}),
    ],
)
def test_generator_31_new_fields(get_create_view_func, field, expected_schema):
    create_view = get_create_view_func(
        'test', DefaultViewSet, 'test', generator_class=RefsSchemaGenerator31
    )
    view = create_view('/test/123/', 'GET')

    result = view.schema._get_field_schema(field)

    assert result == expected_schema


@pytest.mark.parametrize(
    ('generator_class', 'openapi_version', 'expected_openapi_version'),
    [
        (RefsSchemaGenerator, '3.0.2', '3.0.2'),
        (RefsSchemaGenerator, '3.1.0', '3.1.0'),
        (RefsSchemaGenerator30, '3.0.2', '3.0.2'),
        (RefsSchemaGenerator30, '3.1.0', '3.0.2'),
        (RefsSchemaGenerator31, '3.0.2', '3.1.0'),
        (RefsSchemaGenerator31, '3.1.0', '3.1.0'),
    ],
)
def test_settings_default_openapi_version(
    settings, generator_class, openapi_version, expected_openapi_version
):
    settings.API_DEFAULT_OPENAPI_VERSION = openapi_version

    generator = generator_class()

    assert generator.openapi_version == expected_openapi_version

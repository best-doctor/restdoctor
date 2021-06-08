from __future__ import annotations

from rest_framework.fields import Field, FileField

from restdoctor.rest_framework.schema.generators import NewRefsSchemaGenerator
from tests.test_unit.test_schema.stubs import DefaultViewSet

import pytest


@pytest.mark.parametrize(
    'field,expected_schema',
    (
        (Field(allow_null=True), {'type': ['string', 'null']}),
        (FileField(), {'type': 'string', 'contentMediaType': 'application/octet-stream'}),
    ),
)
def test_new_generator_new_fields(get_create_view_func, field, expected_schema):
    create_view = get_create_view_func('test', DefaultViewSet, 'test', generator_class=NewRefsSchemaGenerator)
    view = create_view('/test/123/', 'GET')

    result = view.schema._get_field_schema(field)

    assert result == expected_schema

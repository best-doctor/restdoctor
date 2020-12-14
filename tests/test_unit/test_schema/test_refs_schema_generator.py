import pytest

from restdoctor.rest_framework.schema import RefsSchemaGenerator
from tests.test_unit.test_schema.stubs import DefaultViewSet


@pytest.mark.parametrize(
    'generator,expected_schema_keys',
    (
        (None, ['type', 'properties', 'required']),
        (RefsSchemaGenerator(), ['$ref']),
    ),
)
def test_schema_get_operation_with_refs_schema_generator_success_case(
    get_create_view_func, generator, expected_schema_keys,
):
    create_view = get_create_view_func('test', DefaultViewSet, 'test')

    view = create_view('/test/', 'GET')
    view.schema.generator = generator
    operation = view.schema.get_operation('/test/', 'GET')
    responses_schema = operation['responses']['200']['content']['application/vnd.vendor']['schema']
    responses_properties = responses_schema['properties']['data']
    if 'items' in responses_properties:
        responses_properties = responses_properties['items']

    assert list(responses_properties.keys()) == expected_schema_keys

import pytest

from tests.test_unit.test_schema.stubs import SerializerClassMapViewSet


@pytest.mark.parametrize(
    'path,method,expected_operation_id,expected_responses_required',
    (
        ('/test/', 'GET', 'listLists', ['list_field']),
        ('/test/', 'POST', 'createCreate', ['create_field']),
        ('/test/1234/', 'GET', 'retrieveDefault', ['default_field']),
    ),
)
def test_serializer_class_map_schema(
    path, method, expected_operation_id, expected_responses_required,
    get_create_view_func,
):
    create_view = get_create_view_func('test', SerializerClassMapViewSet, 'test')

    view = create_view(path, method)
    schema = view.schema
    schema.generator = None
    result = view.schema.get_operation(path, method)
    code, _ = view.schema._get_action_code_description(path, method)
    responses_schema = result['responses'][code]['content']['application/vnd.bestdoctor']['schema']
    responses_properties = responses_schema['properties']['data']
    if 'items' in responses_properties:
        responses_properties = responses_properties['items']

    assert result['operationId'] == expected_operation_id
    assert responses_properties['required'] == expected_responses_required

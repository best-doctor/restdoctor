from __future__ import annotations

from tests.test_unit.test_schema.stubs import DefaultViewSet


def test_override_operation_id(get_create_view_func):
    create_view = get_create_view_func('test', DefaultViewSet, 'test')

    view = create_view('/test/', 'GET')
    view.schema_operation_id_map = {'list': 'custom_id'}
    operation = view.schema.get_operation('/test/', 'GET')

    assert operation['operationId'] == 'custom_id'

from __future__ import annotations

from tests.test_unit.test_schema.stubs import MultipleSiblingParametersView


def test_schema_parameters_default_priority(get_create_view_func, settings):
    create_view = get_create_view_func('test', MultipleSiblingParametersView, 'test')
    settings.API_SCHEMA_PRIORITIZE_SERIALIZER_PARAMETERS = False

    view = create_view('/test/', 'GET')
    operation = view.schema.get_operation('/test/', 'GET')

    assert operation['parameters'][2]['description'] == 'filter some field'


def test_schema_parameters_serializer_priority(get_create_view_func, settings):
    create_view = get_create_view_func('test', MultipleSiblingParametersView, 'test')
    settings.API_SCHEMA_PRIORITIZE_SERIALIZER_PARAMETERS = True

    view = create_view('/test/', 'GET')
    operation = view.schema.get_operation('/test/', 'GET')

    assert operation['parameters'][2]['schema']['description'] == 'serializer some field'

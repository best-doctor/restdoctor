import pytest

from restdoctor.rest_framework.schema import RefsSchemaGenerator
from tests.test_unit.test_schema.stubs import DefaultViewSet


@pytest.mark.parametrize(
    'generator,expected_codes',
    (
        (None, ['200']),
        (RefsSchemaGenerator(), ['200', '400', '404']),
    ),
)
def test_errors_handlers_sc(
    get_create_view_func, generator, expected_codes,
):
    create_view = get_create_view_func('test', DefaultViewSet, 'test')

    view = create_view('/test/', 'GET')
    view.schema.generator = generator
    operation = view.schema.get_operation('/test/', 'GET')

    assert list(operation['responses'].keys()) == expected_codes

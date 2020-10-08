import pytest

from restdoctor.rest_framework.routers import ResourceRouter
from restdoctor.rest_framework.schema import ResourceSchema
from tests.test_unit.test_schema.stubs import DefaultAnotherResourceViewSet


@pytest.mark.parametrize(
    'view_class_name,expected_object_name',
    (
        ('PatientView', 'Patient'),
        ('PatientAPIView', 'Patient'),
        ('PatientViewAPIView', 'PatientView'),
        ('PatientResourceViewSet', 'PatientResource'),
    ),
)
def test_resource_schema_object_name_success_case(view_class_name, expected_object_name):
    schema = ResourceSchema()
    view_class = type(view_class_name, (), {})
    schema.view = view_class()

    object_name = schema._get_object_name('/test/', 'GET', 'action')

    assert object_name == expected_object_name


def test_resource_schema_get_response_schema_right_method_success_case(settings, get_create_view_func):
    create_view = get_create_view_func('test', DefaultAnotherResourceViewSet, 'test', router=ResourceRouter())

    view = create_view('/test/', 'GET')
    response_schema = view.schema._get_response_schema('/test/', 'GET')

    assert len(response_schema.get('oneOf', [])) == 2


def test_resource_schema_get_response_schema_wrong_method_success_case(get_create_view_func):
    create_view = get_create_view_func('test', DefaultAnotherResourceViewSet, 'test', router=ResourceRouter())

    view = create_view('/test/', 'POST')
    response_schema = view.schema._get_response_schema('/test/', 'POST')

    print(view.schema._get_resources('POST'))
    print(response_schema)

    assert len(response_schema.get('oneOf', [])) == 0


def test_resource_schema_get_request_body_schema_success_case(get_create_view_func):
    create_view = get_create_view_func(
        'test', DefaultAnotherResourceViewSet, 'test', router=ResourceRouter())

    view = create_view('/test/', 'POST')
    view.resource_discriminate_methods = ['POST']
    request_body = view.schema._get_request_body_schema('/test/', 'POST')

    assert len(request_body.get('oneOf', [])) == 2



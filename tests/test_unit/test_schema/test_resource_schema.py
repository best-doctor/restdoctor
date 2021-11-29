from __future__ import annotations

import pytest

from restdoctor.rest_framework.routers import ResourceRouter
from restdoctor.rest_framework.schema import ResourceSchema
from tests.test_unit.test_schema.stubs import DefaultAnotherResourceViewSet, SingleResourceViewSet


@pytest.mark.parametrize(
    ('view_class_name', 'expected_object_name'),
    [
        ('PatientView', 'Patient'),
        ('PatientAPIView', 'Patient'),
        ('PatientViewAPIView', 'PatientView'),
        ('PatientResourceViewSet', 'PatientResource'),
    ],
)
def test_object_name_success_case(view_class_name, expected_object_name):
    schema = ResourceSchema()
    view_class = type(view_class_name, (), {})
    schema.view = view_class()

    object_name = schema._get_object_name('/test/', 'GET', 'action')

    assert object_name == expected_object_name


@pytest.mark.parametrize(('method'), [('POST'), ('GET')])
def test_get_response_schema_success_case(get_create_view_func, method):
    create_view = get_create_view_func(
        'test', DefaultAnotherResourceViewSet, 'test', router=ResourceRouter()
    )

    view = create_view('/test/', method)
    response_schema = view.schema.get_resources_response_schema('/test/', method)

    assert len(response_schema.get('oneOf', [])) == 2


def test_get_request_body_schema_success_case(get_create_view_func):
    create_view = get_create_view_func(
        'test', DefaultAnotherResourceViewSet, 'test', router=ResourceRouter()
    )

    view = create_view('/test/', 'POST')
    request_body = view.schema.get_resources_request_body_schema('/test/', 'POST')

    assert len(request_body.get('oneOf', [])) == 2


def test_get_responses_success_case(
    get_create_view_func, resource_default_rq_schema, resource_another_rq_schema
):
    create_view = get_create_view_func(
        'test', DefaultAnotherResourceViewSet, 'test', router=ResourceRouter()
    )

    view = create_view('/test/', 'POST')
    responses = view.schema.get_responses('/test/', 'POST')
    responses_codes = set(responses.keys())
    content = responses['201']['content']

    assert responses_codes == {'201', '400', '404'}
    assert content['application/vnd.vendor']['schema']['oneOf'] == [
        resource_default_rq_schema,
        resource_another_rq_schema,
    ]
    assert content['application/vnd.vendor.v1-default']['schema'] == resource_default_rq_schema
    assert content['application/vnd.vendor.v1-another']['schema'] == resource_another_rq_schema
    assert content['application/vnd.vendor.v1-actions']['schema'] == resource_default_rq_schema


def test_get_request_body_success_case(
    get_create_view_func, resource_default_ref, resource_another_ref
):
    create_view = get_create_view_func(
        'test', DefaultAnotherResourceViewSet, 'test', router=ResourceRouter()
    )
    resource_default_wq_ref = resource_default_ref('WQ')
    resource_another_wq_ref = resource_another_ref('WQ')

    view = create_view('/test/', 'POST')
    request_body = view.schema.get_request_body('/test/', 'POST')
    content = request_body['content']

    assert content['application/vnd.vendor']['schema']['oneOf'] == [
        resource_default_wq_ref,
        resource_another_wq_ref,
    ]
    assert content['application/vnd.vendor.v1-default']['schema'] == resource_default_wq_ref
    assert content['application/vnd.vendor.v1-another']['schema'] == resource_another_wq_ref
    assert content['application/vnd.vendor.v1-actions']['schema'] == resource_default_wq_ref


def test_get_action_responses_success_case(get_create_view_func, resource_default_rq_schema):
    create_view = get_create_view_func(
        'test', DefaultAnotherResourceViewSet, 'test', router=ResourceRouter()
    )

    view = create_view('/test/123/custom_action/', 'PUT')
    responses = view.schema.get_responses('/test/123/custom_action/', 'PUT')
    responses_codes = set(responses.keys())
    content = responses['201']['content']

    assert responses_codes == {'201', '400', '404'}
    assert content['application/vnd.vendor']['schema'] == resource_default_rq_schema
    assert 'application/vnd.vendor.v1-default' not in content
    assert 'application/vnd.vendor.v1-another' not in content
    assert content['application/vnd.vendor.v1-actions']['schema'] == resource_default_rq_schema


@pytest.mark.parametrize(
    ('viewset_class'),
    [(DefaultAnotherResourceViewSet), (SingleResourceViewSet)],
    ids=[
        'get params from default viewset in resource',
        'get params from single viewset in resource',
    ],
)
def test_query_params_for_viewset_success_case(get_create_view_func, viewset_class):
    create_view = get_create_view_func('test', viewset_class, 'test', router=ResourceRouter())

    view = create_view('/test/', 'GET')
    view.pagination_class = None
    operation = view.schema.get_operation('/test/', 'GET')
    parameters = operation.get('parameters', [])

    assert parameters != []

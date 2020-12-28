from restdoctor.rest_framework.routers import ResourceRouter
from tests.test_unit.test_schema.stubs import DefaultViewSet, ViewSetWithTags


def test_schema_with_tags_success_case(get_create_view_func):
    create_view = get_create_view_func('test', ViewSetWithTags, 'test')

    view = create_view('/test/', 'GET')
    operation = view.schema.get_operation('/test/', 'GET')

    assert operation['tags'] == ['tag1', 'tag2']


def test_schema_tags_from_path_success_case(get_create_view_func):
    create_view = get_create_view_func('test', DefaultViewSet, 'test')

    view = create_view('/test/', 'GET')
    operation = view.schema.get_operation('/test/', 'GET')

    assert operation['tags'] == ['test']


def test_resource_get_tags_from_default_success_case(get_create_view_func, resource_class, settings):
    settings.API_RESOURCE_DEFAULT = 'default'
    viewset_class = resource_class('default', ViewSetWithTags)
    create_view = get_create_view_func('test', viewset_class, 'test', router=ResourceRouter())

    view = create_view('/test/', 'GET')
    operation = view.schema.get_operation('/test/', 'GET')

    assert operation['tags'] == ['tag1', 'tag2']

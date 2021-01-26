from tests.test_unit.test_schema.stubs import ListViewSetWithRequestSerializer


def test_schema_for_list_viewset(get_create_view_func):
    create_view = get_create_view_func('test', ListViewSetWithRequestSerializer, 'test')

    view = create_view('/test/', 'GET')
    operation = view.schema.get_operation('/test/', 'GET')

    assert operation['parameters'] == [
        {
            'in': 'query',
            'name': 'filter_uuid_field',
            'required': False,
            'schema': {
                'type': 'string',
                'format': 'uuid',
            },
        },
        {
            'in': 'query',
            'name': 'filter_field',
            'required': True,
            'schema': {
                'type': 'string',
                'nullable': True,
                'description': 'Help text',
            },
        },
    ]


def test_get_request_serializer_filter_parameters(get_create_view_func):
    list_view = get_create_view_func('test', ListViewSetWithRequestSerializer, 'test')

    view = list_view('/test/', 'GET')
    parameters = view.schema.get_request_serializer_filter_parameters('/test/', 'GET')

    assert parameters == [
        {
            'in': 'query',
            'name': 'filter_uuid_field',
            'required': False,
            'schema': {
                'type': 'string',
                'format': 'uuid',
            },
        },
        {
            'in': 'query',
            'name': 'filter_field',
            'required': True,
            'schema': {
                'type': 'string',
                'nullable': True,
                'description': 'Help text',
            },
        },
    ]

import pytest
from rest_framework.exceptions import ErrorDetail

from restdoctor.rest_framework.exception_handlers import _get_full_details


@pytest.mark.parametrize(
    ('details', 'expected_result'),
    [
        (ErrorDetail('Empty field', code='blank'), {'message': 'Empty field', 'code': 'blank'}),
        (
            [
                ErrorDetail('Empty field', code='blank'),
                ErrorDetail('Invalid phone', code='invalid'),
            ],
            [
                {'message': 'Empty field', 'code': 'blank'},
                {'message': 'Invalid phone', 'code': 'invalid'},
            ],
        ),
        (
            {
                'phone': [
                    ErrorDetail('Empty field', code='blank'),
                    ErrorDetail('Invalid phone', code='invalid'),
                ],
            },
            [
                {'field': 'phone', 'message': 'Empty field', 'code': 'blank'},
                {'field': 'phone', 'message': 'Invalid phone', 'code': 'invalid'},
            ],
        ),
        (
            {
                'phones.1.phone': [
                    ErrorDetail(string='Empty field', code='blank'),
                    ErrorDetail(string='Invalid phone', code='invalid'),
                ],
                'phones.2.comment': [
                    ErrorDetail(string='Empty field', code='blank'),
                    ErrorDetail(string='Invalid phone', code='invalid'),
                ],
                'phones.3.phone': [
                    ErrorDetail(string='Empty field', code='blank'),
                    ErrorDetail(string='Invalid phone', code='invalid'),
                ],
            },
            [
                {'message': 'Empty field', 'code': 'blank', 'field': 'phones.1.phone'},
                {'message': 'Invalid phone', 'code': 'invalid', 'field': 'phones.1.phone'},
                {'message': 'Empty field', 'code': 'blank', 'field': 'phones.2.comment'},
                {'message': 'Invalid phone', 'code': 'invalid', 'field': 'phones.2.comment'},
                {'message': 'Empty field', 'code': 'blank', 'field': 'phones.3.phone'},
                {'message': 'Invalid phone', 'code': 'invalid', 'field': 'phones.3.phone'},
            ],
        ),
        (
            {
                'phones': [
                    {
                        'phones.1.phone': [
                            ErrorDetail(string='Empty field', code='blank'),
                            ErrorDetail(string='Invalid phone', code='invalid'),
                        ],
                        'phones.2.comment': [
                            ErrorDetail(string='Empty field', code='blank'),
                            ErrorDetail(string='Invalid phone', code='invalid'),
                        ],
                        'phones.3.phone': [
                            ErrorDetail(string='Empty field', code='blank'),
                            ErrorDetail(string='Invalid phone', code='invalid'),
                        ],
                    },
                ],
            },
            [
                {'message': 'Empty field', 'code': 'blank', 'field': 'phones.1.phone'},
                {'message': 'Invalid phone', 'code': 'invalid', 'field': 'phones.1.phone'},
                {'message': 'Empty field', 'code': 'blank', 'field': 'phones.2.comment'},
                {'message': 'Invalid phone', 'code': 'invalid', 'field': 'phones.2.comment'},
                {'message': 'Empty field', 'code': 'blank', 'field': 'phones.3.phone'},
                {'message': 'Invalid phone', 'code': 'invalid', 'field': 'phones.3.phone'},
            ],
        ),
    ],
    ids=[
        'Single error',
        'List of errors',
        'Errors in single field',
        'Errors in multiple fields',
        'Nested errors in multiple fields',
    ],
)
def test__get_full_details(details, expected_result):
    errors_data = _get_full_details(details)

    assert errors_data == expected_result

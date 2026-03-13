from __future__ import annotations

from restdoctor.utils.pydantic import convert_pydantic_errors_to_drf_errors


def test_convert_pydantic_errors_to_drf_errors():
    pydantic_errors = [
        {'loc': ('created_at',), 'msg': 'Input should be a valid datetime', 'type': 'datetime_parsing'},
        {'loc': ('field_a',), 'msg': 'Input should be a valid string', 'type': 'string_type'},
        {
            'loc': ('field_b', 'inner_b'),
            'msg': 'Input should be a valid integer',
            'type': 'int_type',
        },
        {'loc': ('list', 0), 'msg': 'Input should not be None', 'type': 'none_not_allowed'},
    ]
    expected_errors = {
        'created_at': 'Input should be a valid datetime',
        'field_a': 'Input should be a valid string',
        'field_b.inner_b': 'Input should be a valid integer',
        'list.0': 'Input should not be None',
    }
    drf_errors = convert_pydantic_errors_to_drf_errors(pydantic_errors)

    assert drf_errors == expected_errors

from __future__ import annotations

from restdoctor.utils.pydantic import convert_pydantic_errors_to_drf_errors


def test_convert_pydantic_errors_to_drf_errors():
    pydantic_errors = [
        {'loc': ('created_at',), 'msg': 'invalid datetime format', 'type': 'value_error.datetime'},
        {'loc': ('field_a',), 'msg': 'str type expected', 'type': 'type_error.str'},
        {
            'loc': ('field_b', 'inner_b'),
            'msg': 'value is not a valid integer',
            'type': 'type_error.integer',
        },
    ]
    expected_errors = {
        'created_at': 'invalid datetime format',
        'field_a': 'str type expected',
        'field_b.inner_b': 'value is not a valid integer',
    }
    drf_errors = convert_pydantic_errors_to_drf_errors(pydantic_errors)

    assert drf_errors == expected_errors

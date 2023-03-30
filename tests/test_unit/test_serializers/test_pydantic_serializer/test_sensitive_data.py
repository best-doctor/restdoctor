from __future__ import annotations

import pytest

from restdoctor.rest_framework.sensitive_data import (
    clear_sensitive_data,
    get_serializer_sensitive_data_config,
)


def test_get_serializer_sensitive_data_config_pydantic_serializer(
    pydantic_model_serializer_with_sensitive_data,
):
    result = get_serializer_sensitive_data_config(pydantic_model_serializer_with_sensitive_data)

    assert result == {'first_name': True, 'last_name': True}


@pytest.mark.parametrize(
    ('data', 'expected_data'),
    [
        ({'first_name': 'Иван', 'id': 1}, {'first_name': '[Cleaned]', 'id': 1}),
        ({'last_name': 'Иванович', 'id': 1}, {'last_name': '[Cleaned]', 'id': 1}),
        (
            [{'first_name': 'Иван', 'id': 1}, {'first_name': 'Петр', 'id': 2}],
            [{'first_name': '[Cleaned]', 'id': 1}, {'first_name': '[Cleaned]', 'id': 2}],
        ),
    ],
)
def test_clear_sensitive_data_pydantic_serializer(
    data, expected_data, pydantic_model_serializer_with_sensitive_data
):
    result = clear_sensitive_data(data, pydantic_model_serializer_with_sensitive_data)

    assert result == expected_data

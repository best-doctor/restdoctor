from __future__ import annotations

import pytest
from rest_framework.renderers import OpenAPIRenderer

from tests.test_unit.conftest import (
    TestBoolEnum,
    TestComplexEnum,
    TestIntEnum,
    TestStringEnum,
    TestTextChoices,
)


@pytest.mark.parametrize(
    ('test_enum_value', 'expected_result'),
    [
        (TestStringEnum.TEST, 'test'),
        (TestIntEnum.TEST, '1'),
        (TestBoolEnum.TEST, 'true'),
        (TestTextChoices.TEST, 'test'),
        (TestComplexEnum.TEST, "<class 'tests.test_unit.conftest.Class'>"),
    ],
)
def test__open_api_renderer__with_enum(test_enum_value, expected_result):
    renderer = OpenAPIRenderer()

    data = {'enum': [test_enum_value]}

    result = renderer.render(data=data).decode()

    assert result == f'enum:\n- {expected_result}\n'

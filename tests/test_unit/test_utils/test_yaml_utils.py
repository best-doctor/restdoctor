from __future__ import annotations

import io

import pytest
from yaml import Dumper

from restdoctor.utils.yaml_utils import enum_representer
from tests.test_unit.conftest import (
    TestBoolEnum,
    TestComplexEnum,
    TestIntEnum,
    TestStringEnum,
    TestTextChoices,
)


@pytest.mark.parametrize(
    ('test_enum_value', 'expected_result', 'expected_type'),
    [
        (TestStringEnum.TEST, 'test', 'str'),
        (TestIntEnum.TEST, '1', 'int'),
        (TestBoolEnum.TEST, 'true', 'bool'),
        (TestTextChoices.TEST, 'test', 'str'),
        (TestComplexEnum.TEST, "<class 'tests.test_unit.conftest.Class'>", 'str'),
    ],
)
def test__enum_representer(test_enum_value, expected_result, expected_type):
    result = enum_representer(Dumper(stream=io.StringIO()), test_enum_value)

    assert result.value == expected_result
    assert result.tag.endswith(expected_type)

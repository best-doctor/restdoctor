from __future__ import annotations

import typing

import pytest

from restdoctor.utils.typing_inspect import is_list_type, is_optional_type, is_union_type

T = typing.TypeVar('T')


@pytest.mark.parametrize(
    ('annotation', 'expected_result'),
    [
        (typing.Union[int], False),
        (typing.Union[int, int], False),
        (typing.Union, True),
        (typing.Union[T, int], True),
        (typing.Union['T', int], True),
    ],
)
def test_is_union_type(annotation, expected_result):
    result = is_union_type(annotation)

    assert result == expected_result


@pytest.mark.parametrize(
    ('annotation', 'expected_result'),
    [
        (type(None), True),
        (typing.Optional[str], True),
        (typing.Optional[T], True),
        (typing.Optional['T'], True),
        (typing.Union[None], True),
        (typing.Union[int, None], True),
        (typing.Union[T, None], True),
        (typing.Union['T', None], True),
        (typing.Union[int, str], False),
        (typing.Union[T, str], False),
        (typing.Union['T', str], False),
        (typing.Union[int, typing.Optional[str]], True),
    ],
)
def test_is_optional_type(annotation, expected_result):
    result = is_optional_type(annotation)

    assert result == expected_result


@pytest.mark.parametrize(
    ('annotation', 'expected_result'),
    [
        (int, False),
        (dict, False),
        (set, False),
        (list, True),
        (typing.List[int], True),
        (typing.List[T], True),
        (typing.List['T'], True),
        (typing.Optional[list], True),
        (typing.Optional[typing.List], True),
        (typing.Optional[typing.List[T]], True),
        (typing.Optional[set], False),
        (typing.Optional[typing.Set], False),
        (typing.Optional[typing.Set[T]], False),
    ],
)
def test_is_list_type(annotation, expected_result):
    result = is_list_type(annotation)

    assert result == expected_result

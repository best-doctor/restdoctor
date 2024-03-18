from __future__ import annotations

import typing

from pydantic.types import Json


PARAMETRIZE_TYPES = [
    (str, False),
    (int, False),
    (list, True),
    (Json, False),
    (bool, False),
    (typing.List[str], True),
    (typing.Set[int], True),
    (typing.Tuple[typing.List[int]], True),
]

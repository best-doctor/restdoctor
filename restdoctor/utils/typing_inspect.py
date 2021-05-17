from __future__ import annotations

import typing


def is_union_type(tp: typing.Type) -> bool:
    return tp is typing.Union or getattr(tp, '__origin__', None) is typing.Union


def is_optional_type(tp: typing.Type) -> bool:
    if tp is type(None):  # noqa: E721
        return True
    elif is_union_type(tp):
        return any(is_optional_type(tt) for tt in getattr(tp, '__args__', []))
    else:
        return False


def is_list_type(tp: typing.Type) -> bool:
    if tp is list or getattr(tp, '__origin__', None) is list:
        return True
    if is_union_type(tp):
        if (
            len(tp.__args__) == 2
            and is_list_type(tp.__args__[0])
            and is_optional_type(tp.__args__[1])
        ):
            return True
    return False

from __future__ import annotations

import typing


def convert_pydantic_errors_to_drf_errors(
    pydantic_errors: list[dict[str, typing.Any]]
) -> dict[str, str]:
    drf_errors = {}
    for error in pydantic_errors:
        error_loc = error['loc']
        loc_items = (
            (str(item) for item in error_loc) if isinstance(error_loc, (tuple, list)) else error_loc
        )
        drf_errors['.'.join(loc_items)] = error['msg']
    return drf_errors

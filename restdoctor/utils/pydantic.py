from __future__ import annotations

import typing


def convert_pydantic_errors_to_drf_errors(
    pydantic_errors: list[dict[str, typing.Any]]
) -> dict[str, str]:
    drf_errors = {}
    for error in pydantic_errors:
        drf_errors['.'.join(error['loc'])] = error['msg']
    return drf_errors

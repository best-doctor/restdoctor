from __future__ import annotations
from typing import TYPE_CHECKING

from django.conf import settings

if TYPE_CHECKING:
    from typing import Optional
    from restdoctor.utils.custom_types import Prefix, Prefixes, SequenceOrT


def get_api_prefix(default: Optional[Prefix] = '/') -> Optional[Prefix]:
    return get_api_prefixes(default)[0]


def get_api_prefixes(default: Optional[SequenceOrT[Prefix]] = '/') -> Prefixes:
    prefixes = settings.API_PREFIXES or default
    if prefixes is None:
        prefixes = ()
    elif not isinstance(prefixes, tuple):
        prefixes = tuple(prefixes) if isinstance(prefixes, list) else (prefixes,)
    return tuple(
        f'/{prefix.strip("/")}' for prefix in prefixes
    )


def get_api_path_prefix(default: Optional[Prefix] = '/') -> Optional[Prefix]:
    return get_api_path_prefixes(default)[0]


def get_api_path_prefixes(default: Optional[SequenceOrT[Prefix]] = '/') -> Prefixes:
    prefixes = settings.API_PREFIXES or default
    if prefixes is None:
        prefixes = ()
    elif not isinstance(prefixes, tuple):
        prefixes = tuple(prefixes) if isinstance(prefixes, list) else (prefixes,)
    return tuple(
        f'{prefix.strip("/")}/' for prefix in prefixes
    )

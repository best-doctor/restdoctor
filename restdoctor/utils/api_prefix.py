from __future__ import annotations
from typing import TYPE_CHECKING

from django.conf import settings

if TYPE_CHECKING:
    from typing import Optional
    from restdoctor.utils.custom_types import Prefix, Prefixes, SequenceOrT


def get_api_prefix(default: Optional[Prefix] = '/') -> Optional[Prefix]:
    try:
        api_prefix = settings.API_PREFIX
        return f'/{api_prefix.strip("/")}'
    except (KeyError, AttributeError):
        return default


def get_api_prefixes(default: Optional[SequenceOrT[Prefix]] = '/') -> Prefixes:
    prefixes = getattr(settings, 'API_PREFIXES', default) or default
    if prefixes is None:
        prefixes = ()
    elif not isinstance(prefixes, tuple):
        prefixes = tuple(prefixes) if isinstance(prefixes, list) else (prefixes,)
    return tuple(
        f'/{prefix.strip("/")}' for prefix in prefixes
    )


def get_api_path_prefix(default: Optional[Prefix] = '/') -> Optional[Prefix]:
    try:
        api_prefix = settings.API_PREFIX
        return f'{api_prefix.strip("/")}/'
    except (KeyError, AttributeError):
        return default


def get_api_path_prefixes(default: Optional[SequenceOrT[Prefix]] = '/') -> Prefixes:
    prefixes = getattr(settings, 'API_PREFIXES', default) or default
    if prefixes is None:
        prefixes = ()
    elif not isinstance(prefixes, tuple):
        prefixes = tuple(prefixes) if isinstance(prefixes, list) else (prefixes,)
    return tuple(
        f'{prefix.strip("/")}/' for prefix in prefixes
    )

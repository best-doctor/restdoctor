from __future__ import annotations
import typing as t

GenericContext = t.Dict[str, t.Any]
ImmutableContext = t.Mapping[str, t.Any]

T = t.TypeVar('T')

SequenceOrT = t.Union[t.Sequence[T], T]

Prefix = str
Prefixes = t.Tuple[Prefix, ...]

MappingSet = t.Set[str]
OptionalMappingSet = t.Optional[MappingSet]

InitKwargs = t.Dict[str, t.Any]
OptionalInitKwargs = t.Optional[InitKwargs]

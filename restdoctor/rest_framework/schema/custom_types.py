from __future__ import annotations
import typing as t

OpenAPISchema = t.Dict[str, 'OpenAPISchema']  # type: ignore
LocalRefs = t.Dict[t.Tuple[str, ...], t.Any]

ResponseCode = str
ActionDescription = str

CodeActionSchemaTuple = t.Tuple[ResponseCode, ActionDescription, t.Optional[OpenAPISchema]]  # type: ignore
CodeDescriptionTuple = t.Tuple[ResponseCode, ActionDescription]

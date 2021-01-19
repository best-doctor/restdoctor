from __future__ import annotations
import functools
import typing

from django.core.exceptions import ImproperlyConfigured

from restdoctor.rest_framework.schema.constants import ACTION_CODES_MAP

if typing.TYPE_CHECKING:
    from rest_framework.generics import GenericAPIView
    from restdoctor.rest_framework.custom_types import Action
    from restdoctor.rest_framework.schema.custom_types import (
        ActionDescription, CodeActionSchemaTuple, ResponseCode, OpenAPISchema,
    )

    ActionSchemaTuple = typing.Tuple[ActionDescription, typing.Optional[OpenAPISchema]]
    ActionSchema = typing.Union[ActionDescription, ActionSchemaTuple]
    OptionalActionSchema = typing.Optional[ActionSchema]
    CodeSchemasMap = typing.Dict[ResponseCode, OptionalActionSchema]
    ActionCodesMap = typing.Dict[Action, CodeSchemasMap]


@functools.lru_cache()
def get_action(path: str, method: str, view: GenericAPIView) -> str:
    action = getattr(view, 'action', None)
    if action:
        return action
    action_map = getattr(view, 'action_map', None) or {}
    method_name = method.lower()
    return action_map.get(method_name, method_name)


def normalize_action_schema(code: str, action_schema: ActionSchema) -> CodeActionSchemaTuple:
    if isinstance(action_schema, str):
        return code, action_schema, None
    description, schema = action_schema
    return code, description, schema


def get_action_map_kwargs(
    action: str, action_codes_map: typing.Optional[ActionCodesMap],
) -> typing.List[typing.Tuple[str, ActionCodesMap]]:
    kwargs_variants = []
    kwargs_use_defaults = True
    if isinstance(action_codes_map, dict):
        kwargs_variants.extend([
            (action, action_codes_map),
            ('default', action_codes_map),
        ])
        if action_codes_map.get('default', {}) is None:
            kwargs_use_defaults = False
    if kwargs_use_defaults:
        kwargs_variants.extend([
            (action, ACTION_CODES_MAP),
            ('default', ACTION_CODES_MAP),
        ])
    return kwargs_variants


def get_action_code_schemas_from_map(
    action: str, action_codes_map: ActionCodesMap,
) -> typing.Iterator[typing.Tuple[str, OptionalActionSchema]]:
    action_codes = action_codes_map.get(action, {})

    if isinstance(action_codes, set):
        raise ImproperlyConfigured(
            f'schema_action_codes_map item should be dict for action {action}: {action_codes}')

    for code, action_schema in action_codes.items():
        yield code, action_schema

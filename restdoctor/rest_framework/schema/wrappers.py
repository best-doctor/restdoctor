from __future__ import annotations

import typing

from rest_framework.fields import Field


class SchemaWrapper(Field):
    def __new__(
        cls, wrapped: Field, schema_type: typing.Union[Field, typing.Type[Field]] = None,
    ) -> Field:
        if isinstance(schema_type, type):
            schema_type = schema_type()
        wrapped.schema_type = schema_type
        return wrapped

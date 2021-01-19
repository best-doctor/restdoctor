from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from restdoctor.rest_framework.schema.custom_types import LocalRefs, OpenAPISchema


class LocalRefsRegistry:
    def __init__(self) -> None:
        self._local_refs: LocalRefs = {}

    def put_local_ref(self, ref: str, schema: OpenAPISchema) -> None:
        if ref.startswith('#/components'):
            path = tuple(ref.split('/')[2:])
            self._local_refs[path] = schema

    def get_components(self) -> OpenAPISchema:
        components: OpenAPISchema = {}
        for path, schema in self._local_refs.items():
            component = components
            for path_item in path[:-1]:
                try:
                    component = component[path_item]
                except KeyError:
                    components[path_item] = {}
                    component = component[path_item]
            component[path[-1]] = schema
        return components

from __future__ import annotations
import copy
import typing
from rest_framework.routers import BaseRouter, SimpleRouter, Route

from restdoctor.rest_framework.resources import ResourceViewSet
from restdoctor.utils.constants import IDENTIFIER_REGEX, DEFAULT_MAPPING_SET

if typing.TYPE_CHECKING:
    from restdoctor.rest_framework.viewsets import ViewSetMixin

    from restdoctor.django.custom_types import URLPatternList
    from restdoctor.rest_framework.custom_types import RouteOrDynamicRouteList
    from restdoctor.utils.custom_types import OptionalMappingSet, OptionalInitKwargs

    MethodMap = typing.Dict[str, str]


class ResourceRouter(SimpleRouter):
    def get_method_map(self, viewset: ViewSetMixin, method_map: MethodMap) -> MethodMap:
        if not issubclass(viewset, ResourceViewSet):
            return super().get_method_map(viewset, method_map)

        actions = viewset.get_action_methods() + viewset.get_extra_actions()
        bound_methods = {}
        for method, action in method_map.items():
            if action in actions:
                bound_methods[method] = action
        return bound_methods


class TreeMixin(BaseRouter):
    def __init__(  # noqa: CFQ002
        self,
        parent_router: typing.Optional[BaseRouter] = None,
        parent_prefix: typing.Optional[str] = None,
        parent_viewset: typing.Any = None,
        mapping_set: OptionalMappingSet = None,
        initkwargs: OptionalInitKwargs = None,
        *args: typing.Any, **kwargs: typing.Any,
    ) -> None:
        self.nest_count = 0
        self.children: typing.List[TreeMixin] = []
        if parent_router:
            self.parent_router = parent_router
            self.nest_count = getattr(parent_router, 'nest_count', 0) + 1
            self.nest_prefix = kwargs.pop('lookup', 'nested_%i' % self.nest_count) + '_'

        super().__init__(*args, **kwargs)

        if not parent_router or not parent_prefix:
            return

        mapping_set = (mapping_set or DEFAULT_MAPPING_SET) & DEFAULT_MAPPING_SET

        if 'trailing_slash' not in kwargs:
            self.trailing_slash = parent_router.trailing_slash

        self.check_valid_name(self.nest_prefix)

        nested_routes: RouteOrDynamicRouteList = []
        parent_lookup_regex = parent_router.get_lookup_regex(parent_viewset, self.nest_prefix)

        self.parent_regex = f'{parent_prefix}/{parent_lookup_regex}/'

        self.routes: RouteOrDynamicRouteList
        for route in self.routes:
            initkwargs = copy.deepcopy(initkwargs or {})

            initkwargs.update(route.initkwargs)
            route_contents = route._asdict()
            escaped_parent_regex = self.parent_regex.replace('{', '{{').replace('}', '}}')
            route_contents['url'] = route.url.replace('^', '^' + escaped_parent_regex)
            route_contents['initkwargs'] = initkwargs
            # WIP: need the way to filter out some nested endpoints
            if isinstance(route, Route):
                mapping = {
                    method: view_function
                    for method, view_function in route.mapping.items()
                    if view_function in mapping_set
                }
                route_contents['mapping'] = mapping
            nested_routes.append(type(route)(**route_contents))

        self.routes = nested_routes

    def check_valid_name(self, value: str) -> None:
        if IDENTIFIER_REGEX.match(value) is None:
            raise ValueError(f"lookup argument '{value}' needs to be valid python identifier")

    def register_child(  # noqa: CFQ002
        self,
        prefix: str,
        viewset: typing.Any,
        basename: str,
        lookup: str,
        *args: typing.Any, **kwargs: typing.Any,
    ) -> TreeMixin:
        super().register(prefix, viewset, basename=basename)

        kwargs['parent_router'] = self
        kwargs['parent_prefix'] = prefix
        kwargs['parent_viewset'] = viewset
        kwargs['lookup'] = lookup
        child_router = self.__class__(*args, **kwargs)

        self.children.append(child_router)
        return child_router


class TreeRouter(TreeMixin, SimpleRouter):
    def get_urls(self) -> URLPatternList:
        urls = super().get_urls()
        for child in self.children:
            urls.extend(child.urls)

        return urls

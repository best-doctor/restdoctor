from __future__ import annotations
import typing as t

from django.db import models
from rest_framework.parsers import BaseParser
from rest_framework.renderers import BaseRenderer
from rest_framework.response import Response
from rest_framework.routers import DynamicRoute, Route
from rest_framework.viewsets import ViewSet

OpenAPISchema = t.Dict[str, 'OpenAPISchema']  # type: ignore
LocalRefs = t.Dict[t.Tuple[str, ...], t.Any]

CodesTuple = t.Tuple[str, str]
ActionCodesMap = t.Dict[str, CodesTuple]

ActionMap = t.Dict[str, str]
Handler = t.Callable[..., Response]
ResourceExtraAction = t.Tuple[str, str, Handler]

RouteOrDynamicRoute = t.Union[Route, DynamicRoute]
RouteOrDynamicRouteList = t.List[RouteOrDynamicRoute]

Parsers = t.Sequence[BaseParser]
OptionalParser = t.Optional[BaseParser]

Renderers = t.Sequence[BaseRenderer]
OptionalRenderer = t.Optional[BaseRenderer]

ResourceMapElement = t.TypeVar('ResourceMapElement')
ResourceMap = t.Dict[str, ResourceMapElement]

ResourceViewsMap = ResourceMap[t.Type[ViewSet]]
ResourceActionsMap = ResourceMap[t.Set[str]]
ResourceHandlersMap = ResourceMap[Handler]
ResourceModelsMap = ResourceMap[t.Optional[models.Model]]

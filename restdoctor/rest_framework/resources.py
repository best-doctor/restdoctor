from __future__ import annotations

import collections
import functools
import inspect
import logging
import typing

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Manager, QuerySet
from django.http import Http404
from rest_framework.exceptions import MethodNotAllowed, NotFound

from restdoctor.rest_framework.generics import GenericAPIView
from restdoctor.rest_framework.pagination import PageNumberPagination
from restdoctor.rest_framework.schema import ResourceSchema
from restdoctor.rest_framework.viewsets import GenericViewSet

if typing.TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from rest_framework.pagination import BasePagination
    from rest_framework.response import Response

    from restdoctor.rest_framework.custom_types import (
        ActionMap,
        Handler,
        ResourceActionsMap,
        ResourceExtraAction,
        ResourceHandlersMap,
        ResourceModelsMap,
        ResourceViewsMap,
    )

logger = logging.getLogger(__name__)


def _is_extra_action(attr: typing.Any) -> bool:
    return hasattr(attr, 'mapping')


def get_queryset_model_map(resource_views_map: ResourceViewsMap) -> ResourceModelsMap:
    models_map: ResourceModelsMap = {}

    for resource, viewset_class in resource_views_map.items():
        queryset = getattr(viewset_class, 'queryset', None)
        if isinstance(queryset, (Manager, QuerySet)):
            models_map[resource] = queryset.model
        else:
            models_map[resource] = None

    return models_map


def merge_actions(handlers_actions: typing.Sequence[typing.Optional[ActionMap]]) -> ActionMap:
    actions = {}
    for handler_actions in handlers_actions:
        if handler_actions:
            actions.update(handler_actions)
    return actions


def filter_actions_by_handlers(action_map: ActionMap, handlers: typing.Set[str]) -> ActionMap:
    return {action: handler for action, handler in action_map.items() if handler in handlers}


class ResourceBase:
    schema_class = ResourceSchema

    default_discriminative_value = settings.API_RESOURCE_DEFAULT
    resource_discriminative_param = settings.API_RESOURCE_DISCRIMINATIVE_PARAM
    resource_views_map: ResourceViewsMap = {}
    resource_actions_map: ResourceActionsMap = {}
    resource_handlers_map: ResourceHandlersMap = {}

    resource_discriminate_methods = ['GET']

    @property
    def schema_tags(self) -> typing.List[str]:
        default_view = self.resource_views_map.get(self.default_discriminative_value)
        return getattr(default_view, 'schema_tags', [])

    @classmethod
    def get_resource_handlers(cls, **initkwargs: typing.Any) -> ResourceHandlersMap:
        return {
            resource: viewset.as_view(**initkwargs)
            for resource, viewset in cls.resource_views_map.items()
        }

    @classmethod
    def as_view(cls, **initkwargs: typing.Any) -> typing.Any:
        cls.check_queryset_models()
        resource_handlers_map = cls.get_resource_handlers(**initkwargs)
        view = super().as_view(resource_handlers_map=resource_handlers_map, **initkwargs)  # type: ignore
        return view

    @classmethod
    @functools.lru_cache
    def check_queryset_models(cls) -> bool:
        warnings: typing.List[str] = []
        errors: typing.List[str] = []
        models_map = get_queryset_model_map(cls.resource_views_map)
        current_model = None
        for resource, model in models_map.items():
            if model is None:
                warnings.append(f'Resource {resource} for {cls.__name__} has no queryset.')
            elif current_model is None:
                current_model = model
            elif current_model != model:
                errors.append(
                    (
                        f'Resource {resource} for {cls.__name__} has wrong queryset model '
                        f'{model} instead of {current_model}.'
                    )
                )
        for warning in warnings:
            logger.warning(warning)
        if errors:
            raise ImproperlyConfigured(','.join(errors))
        return True

    def get_discriminant(self, request: WSGIRequest) -> str:
        try:
            if request.api_params.resource_discriminator:
                return request.api_params.resource_discriminator
        except AttributeError:
            pass

        if request.method in self.resource_discriminate_methods:
            discriminant = (
                request.GET.get(self.resource_discriminative_param)
                or self.default_discriminative_value
            )
            if settings.API_RESOURCE_SET_PARAM and (
                discriminant != self.default_discriminative_value
                or settings.API_RESOURCE_SET_PARAM_FOR_DEFAULT
            ):
                request.resource_args = {self.resource_discriminative_param: discriminant}
            return discriminant
        return self.default_discriminative_value

    def dispatch(self, request: WSGIRequest, *args: typing.Any, **kwargs: typing.Any) -> Response:
        discriminant = self.get_discriminant(request)

        resource_dispatch = self.resource_handlers_map.get(discriminant)
        if resource_dispatch:
            return resource_dispatch(request, *args, **kwargs)
        raise Http404()


class ResourceViewSet(ResourceBase, GenericViewSet):
    pagination_class: typing.Optional[BasePagination] = PageNumberPagination

    def __init__(
        self,
        resource_handlers_map: typing.Dict[str, Handler] = None,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.resource_handlers_map = resource_handlers_map or {}
        for method in self.get_action_methods():
            if not hasattr(self, method):
                setattr(self, method, lambda a: None)

    @classmethod
    def get_resource_handlers(
        cls, actions: ActionMap = None, **initkwargs: typing.Any
    ) -> ResourceHandlersMap:
        actions = actions or {}
        resource_actions_map = cls.get_resource_actions_map()
        resource_handlers = {}
        for resource, viewset in cls.resource_views_map.items():
            resource_actions = filter_actions_by_handlers(
                actions, resource_actions_map.get(resource, set())
            )
            if resource_actions:
                resource_handlers[resource] = viewset.as_view(
                    actions=resource_actions, **initkwargs
                )
        return resource_handlers

    @classmethod
    def as_view(cls, actions: ActionMap = None, **initkwargs: typing.Any) -> typing.Any:
        initkwargs['actions'] = actions
        return super().as_view(**initkwargs)

    @classmethod
    def get_resource_actions_map(cls) -> ResourceActionsMap:
        if not cls.resource_actions_map:
            resource_actions_map = collections.defaultdict(set)

            for actions_list_func in cls.resources_actions, cls.resources_extra_actions:
                for resource, name, _ in actions_list_func():
                    resource_actions_map[resource].add(name)

            cls.resource_actions_map = resource_actions_map
        return cls.resource_actions_map

    @classmethod
    def get_action_methods(cls) -> typing.List[str]:
        available_methods_set = set()
        for action_map in cls.get_resource_actions_map().values():
            available_methods_set.update(action_map)

        return list(available_methods_set)

    @classmethod
    def gen_resources_actions(cls) -> typing.Iterator[ResourceExtraAction]:
        crud_methods_set = {'list', 'retrieve', 'create', 'update', 'partial_update', 'destroy'}
        for resource, viewset_class in cls.resource_views_map.items():
            for name in crud_methods_set:
                handler = getattr(viewset_class, name, None)
                if handler:
                    yield resource, name, handler

    @classmethod
    @functools.lru_cache
    def resources_actions(cls) -> typing.List[ResourceExtraAction]:
        return list(cls.gen_resources_actions())

    @classmethod
    def gen_resources_extra_actions(cls) -> typing.Iterator[ResourceExtraAction]:
        for resource, viewset_class in cls.resource_views_map.items():
            for name, handler in inspect.getmembers(viewset_class, _is_extra_action):
                yield resource, name, handler

    @classmethod
    @functools.lru_cache
    def resources_extra_actions(cls) -> typing.List[ResourceExtraAction]:
        return list(cls.gen_resources_extra_actions())

    @classmethod
    def get_extra_actions(cls) -> typing.List[Handler]:
        return [handler for _, _, handler in cls.resources_extra_actions()]

    def dispatch(self, request: WSGIRequest, *args: typing.Any, **kwargs: typing.Any) -> Response:
        discriminator = self.get_discriminant(request)

        method = request.method.lower()
        action = self.action_map.get(method)
        actions = self.resource_actions_map.get(discriminator)
        if actions is None:
            exc = NotFound()
        elif action in actions:
            return super().dispatch(request, *args, **kwargs)
        else:
            exc = MethodNotAllowed(request.method)
        return self.exception_response(exc, request, *args, **kwargs)

    def exception_response(
        self, exc: Exception, request: WSGIRequest, *args: typing.Any, **kwargs: typing.Any
    ) -> Response:
        request = self.initialize_request(request, *args, **kwargs)
        self.headers = self.default_response_headers
        response = self.handle_exception(exc)
        return self.finalize_response(request, response, *args, **kwargs)


class ResourceView(ResourceBase, GenericAPIView):
    @classmethod
    def as_view(cls, **initkwargs: typing.Any) -> typing.Any:
        view = super().as_view(**initkwargs)
        resource_handlers_map = view.initkwargs.get('resource_handlers_map', {})
        actions = merge_actions(
            [getattr(handler, 'actions', None) for handler in resource_handlers_map.values()]
        )
        if actions:
            view.actions = actions
        return view

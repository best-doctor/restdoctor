from __future__ import annotations

import contextlib
import typing

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404

from restdoctor.rest_framework.generics import GenericAPIView
from restdoctor.rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from restdoctor.rest_framework.sensitive_data import clear_sensitive_data
from restdoctor.rest_framework.signals import bind_extra_request_view_initial_metadata
from restdoctor.utils.permissions import get_permission_classes_from_map
from restdoctor.utils.serializers import get_serializer_class_from_map
from restdoctor.utils.structlog import get_logger

if typing.TYPE_CHECKING:
    from django.core.handlers.wsgi import WSGIRequest
    from django.http import HttpRequest
    from rest_framework.permissions import BasePermission
    from rest_framework.request import Request
    from rest_framework.response import Response
    from rest_framework.serializers import BaseSerializer

    from restdoctor.rest_framework.sensitive_data import SerializerData
    from restdoctor.utils.serializers import SerializerType


logger = get_logger(__name__)


class SerializerClassMapApiView(GenericAPIView):
    action_map: typing.Dict[str, str] = {}
    action: str = ''
    permission_classes_map: typing.Dict[str, typing.List[BasePermission]]

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        if 'permission_classes' in kwargs and getattr(self, 'permission_classes_map', None):
            raise ImproperlyConfigured('Use permission_classes_map')
        super().__init__(*args, **kwargs)

    @classmethod
    def as_view(cls, **initkwargs: typing.Any) -> SerializerClassMapApiView:
        view = super().as_view(**initkwargs)
        if cls.action_map:
            view.actions = cls.action_map
        return view

    def dispatch(self, request: WSGIRequest, *args: typing.Any, **kwargs: typing.Any) -> Response:
        response = super().dispatch(request, *args, **kwargs)
        response.serializer = self.get_response_serializer_class()
        return response

    def clear_request_data(self, request: Request) -> typing.Optional[SerializerData]:
        request_serializer = self.get_request_serializer_class()
        request_data = request.data
        if request_data and request_serializer:
            return clear_sensitive_data(request_data, request_serializer)
        return None

    def initial(self, request: Request, *args: typing.Any, **kwargs: typing.Any) -> None:
        if settings.API_ENABLE_STRUCTLOG:
            bind_extra_request_view_initial_metadata.send(
                sender=self.__class__, request=request, logger=logger
            )
            try:
                request_data = self.clear_request_data(request)
            except Exception:
                request_data = None

            logger.info(
                'view_initial',
                app_name=self.__module__.split('.')[0],
                module=self.__module__,
                view_name=self.__class__.__name__,
                request_data=request_data,
                request_query_params=dict(request.query_params),
                action=self.get_action(),
            )
        super().initial(request, *args, **kwargs)

    def get_action(self) -> str:
        action = getattr(self, 'action', None)
        if action:
            return action
        if self.request:
            return self.request.method.lower()
        return 'default'

    def get_permissions(self) -> typing.List[BasePermission]:
        permission_classes = get_permission_classes_from_map(
            action=self.get_action(),
            permission_classes_map=getattr(self, 'permission_classes_map', {}),
            default_permission_classes=self.permission_classes,
        )
        return [permission() for permission in permission_classes]

    def get_serializer_class(
        self,
        stage: str = 'response',
        action: str = None,
        api_format: str = None,
        use_default: bool = True,
    ) -> SerializerType:
        action = action or self.get_action()
        serializer_class_map = getattr(self, 'serializer_class_map', {})

        if api_format is None:
            api_format = settings.API_DEFAULT_FORMAT
            with contextlib.suppress(AttributeError):
                api_format = self.request.api_params.format or api_format

        return get_serializer_class_from_map(
            action,
            stage,
            serializer_class_map,
            self.serializer_class,
            use_default=use_default,
            api_format=api_format,
        )

    def get_serializer_context(self, stage: str = 'response') -> typing.Dict[str, typing.Any]:
        return super().get_serializer_context()

    def get_serializer_instance(
        self, serializer_class: SerializerType, *args: typing.Any, **kwargs: typing.Any
    ) -> BaseSerializer:
        stage = kwargs.pop('stage', 'response')
        kwargs['context'] = self.get_serializer_context(stage)
        return serializer_class(*args, **kwargs)

    def get_request_serializer_class(self, use_default: bool = True) -> SerializerType:
        return self.get_serializer_class('request', use_default=use_default)

    def get_response_serializer_class(self) -> SerializerType:
        return self.get_serializer_class('response')

    def get_meta_serializer_class(self) -> SerializerType:
        return self.get_serializer_class('meta', use_default=False)

    def get_request_serializer(
        self, *args: typing.Any, use_default: bool = True, **kwargs: typing.Any
    ) -> BaseSerializer:
        stage = 'request'
        serializer_class = self.get_serializer_class(stage, use_default=use_default)
        return self.get_serializer_instance(serializer_class, stage=stage, *args, **kwargs)

    def get_response_serializer(self, *args: typing.Any, **kwargs: typing.Any) -> BaseSerializer:
        stage = 'response'
        serializer_class = self.get_serializer_class(stage)
        return self.get_serializer_instance(serializer_class, stage=stage, *args, **kwargs)

    def get_meta_serializer(self, *args: typing.Any, **kwargs: typing.Any) -> BaseSerializer:
        stage = 'meta'
        serializer_class = self.get_meta_serializer_class()
        return self.get_serializer_instance(serializer_class, stage=stage, *args, **kwargs)


class ListAPIView(ListModelMixin, SerializerClassMapApiView):
    action_map = {'get': 'list'}

    def get(self, request: HttpRequest, *args: typing.Any, **kwargs: typing.Any) -> Response:
        self.action = 'list'
        return self.list(request, *args, **kwargs)


class RetrieveAPIView(RetrieveModelMixin, SerializerClassMapApiView):
    action_map = {'get': 'retrieve'}

    def get(self, request: HttpRequest, *args: typing.Any, **kwargs: typing.Any) -> Response:
        self.action = 'retrieve'
        return self.retrieve(request, *args, **kwargs)


class NotFound(GenericAPIView):
    def get(self, request: HttpRequest, *args: typing.Any, **kwargs: typing.Any) -> Response:
        raise Http404(f'Resource {request.path} not found')

from __future__ import annotations

import re
import contextlib
from typing import Optional, Dict

from django.core.exceptions import (
    ObjectDoesNotExist, ValidationError as DjangoValidationError, ImproperlyConfigured,
)
from django.db.models import Model
from django.http import Http404
from rest_framework.generics import GenericAPIView as BaseGenericAPIView

from restdoctor.rest_framework.mixins import NegotiatedMixin


class GenericAPIView(NegotiatedMixin, BaseGenericAPIView):
    lookup_fields: Optional[Dict[str, str]] = None

    def get_object(self) -> Model:
        if self.lookup_fields is None:
            return super().get_object()

        self._check_lookup_configuration()
        queryset = self.filter_queryset(self.get_queryset())

        obj = None
        filter_value = self.kwargs[self.lookup_url_kwarg]
        for lookup_field, lookup_regex in self.lookup_fields.items():
            if re.match(lookup_regex, filter_value):
                filter_kwargs = {lookup_field: filter_value}
                with contextlib.suppress(
                    AttributeError, TypeError, ValueError, DjangoValidationError, ObjectDoesNotExist,
                ):
                    obj = queryset.get(**filter_kwargs)

        if obj is None:
            raise Http404

        self.check_object_permissions(self.request, obj)

        return obj

    def _check_lookup_configuration(self) -> None:
        if not self.lookup_url_kwarg:
            raise ImproperlyConfigured((
                f'View {self.__class__.__name__} improperly configured. '
                f'Set the `.lookup_url_kwarg` with `.lookup_fields`'
            ))

        if self.lookup_url_kwarg not in self.kwargs:
            raise ImproperlyConfigured((
                f'Expected view {self.__class__.__name__} to be called with a URL keyword argument '
                f'named "{self.lookup_url_kwarg}". Fix your URL conf, or set the `.lookup_field` '
                f'attribute on the view correctly.'
            ))

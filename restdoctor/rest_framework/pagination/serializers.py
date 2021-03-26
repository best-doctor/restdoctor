from __future__ import annotations
import typing

from django.utils.translation import gettext_lazy as _
from rest_framework.fields import IntegerField, UUIDField, BooleanField, CharField
from rest_framework.serializers import Serializer

from restdoctor.constants import DEFAULT_PAGE_SIZE, DEFAULT_MAX_PAGE_SIZE


class PerPageSerializerBase(Serializer):
    per_page = IntegerField(default=DEFAULT_PAGE_SIZE, allow_null=True,
                            help_text='Количество элементов на странице')

    def __init__(
        self, max_per_page: int = 200,
        *args: typing.Any, **kwargs: typing.Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.max_per_page = max_per_page

    def validate_per_page(self, value: typing.Optional[int]) -> int:
        if value is None:
            return DEFAULT_PAGE_SIZE
        if value > self.max_per_page:
            return self.max_per_page
        return value


class PageNumberRequestSerializer(PerPageSerializerBase):
    page = IntegerField(min_value=1, default=1, help_text='Выбранная страница, начиная с 1')


class PageNumberUncountedResponseSerializer(Serializer):
    page = IntegerField(min_value=1, help_text=_('Selected page'))
    per_page = IntegerField(
        required=True, max_value=DEFAULT_MAX_PAGE_SIZE,
        help_text=_('Page size'),
    )
    has_next = BooleanField(help_text=_('Has result next page'))
    url = CharField(help_text=_('Current page URL'))
    next_url = CharField(help_text=_('Next page URL'), allow_null=True)
    prev_url = CharField(help_text=_('Previous page URL'), allow_null=True)


class PageNumberResponseSerializer(PageNumberUncountedResponseSerializer):
    total = IntegerField(help_text=_('Total result size'))
    last_url = CharField(help_text=_('Last page URL'), allow_null=True)


class CursorUUIDRequestSerializer(PerPageSerializerBase):
    after = UUIDField(required=False, allow_null=True, help_text=_('After UUID'))
    before = UUIDField(required=False, allow_null=True, help_text=_('Before UUID'))


class CursorUUIDUncountedResponseSerializer(Serializer):
    after = UUIDField(required=False, allow_null=True, help_text=_('After UUID'))
    before = UUIDField(required=False, allow_null=True, help_text=_('Before UUID'))
    per_page = IntegerField(
        required=True, max_value=DEFAULT_MAX_PAGE_SIZE,
        help_text=_('Page size'),
    )
    has_next = BooleanField(help_text=_('Has result next page'))
    url = CharField(help_text=_('Current page URL'))
    after_url = CharField(help_text=_('URL of page after cursor position'), allow_null=True)
    before_url = CharField(help_text=_('URL of page before cursor position'), allow_null=True)


class CursorUUIDResponseSerializer(CursorUUIDUncountedResponseSerializer):
    total = IntegerField(help_text=_('Total result size'))
    last_url = CharField(help_text=_('Last page URL'), allow_null=True)

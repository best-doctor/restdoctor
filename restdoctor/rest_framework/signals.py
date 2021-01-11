from __future__ import annotations

from django.dispatch import Signal

bind_extra_request_view_initial_metadata = Signal(providing_args=['request', 'logger'])

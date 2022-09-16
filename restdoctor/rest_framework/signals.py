from __future__ import annotations

from django.dispatch import Signal

# Arguments: request, logger, view_instance
bind_extra_request_view_initial_metadata = Signal()

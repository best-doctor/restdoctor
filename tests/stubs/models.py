import uuid

from django.db import models
from django.utils import timezone


class MyModel(models.Model):
    class Meta:
        app_label = 'restdoctor'

    uuid = models.UUIDField(  # null_for_compatibility
        default=uuid.uuid4, editable=False, null=True, unique=True)
    timestamp = models.DateTimeField('Event timestamp', default=timezone.localtime)

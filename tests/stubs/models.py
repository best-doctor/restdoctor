import uuid

from django.db import models
from django.utils import timezone


class MyModel(models.Model):
    class Meta:
        app_label = 'restdoctor'

    uuid = models.UUIDField(  # null_for_compatibility
        default=uuid.uuid4, editable=False, null=True, unique=True
    )
    timestamp = models.DateTimeField('Event timestamp', default=timezone.localtime)


class MyAnotherModel(models.Model):
    class Meta:
        app_label = 'restdoctor'

    uuid = models.UUIDField(  # null_for_compatibility
        verbose_name='UUID', default=uuid.uuid4, editable=False, null=True, unique=True
    )
    timestamp = models.DateTimeField('Another Event timestamp', default=timezone.localtime)
    my_model = models.ForeignKey(MyModel, verbose_name='My Model', on_delete=models.CASCADE)


class MyAnotherOneModel(models.Model):
    class Meta:
        app_label = 'restdoctor'

    my_another_model = models.OneToOneField(
        MyAnotherModel,
        verbose_name='My Another Model',
        related_name='my_another_one_model',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    timestamp = models.DateTimeField('Another One Event timestamp', default=timezone.localtime)

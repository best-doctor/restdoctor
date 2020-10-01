from factory.django import DjangoModelFactory

from tests.stubs.models import MyModel


class MyModelFactory(DjangoModelFactory):
    class Meta:
        model = MyModel

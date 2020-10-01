import os

import django
from django.test.utils import setup_databases


def pytest_configure(config):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
    django.setup()
    setup_databases(verbosity=1, interactive=False)

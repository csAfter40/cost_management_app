from django.test.runner import DiscoverRunner
from django.test.utils import override_settings
import logging

TEST_SETTINGS = {}

class CustomRunner(DiscoverRunner):
    """
    Custom test runner for disabling logs during tests and overriding 
    settings.py file with test settings.
    """
    def run_tests(self, *args, **kwargs):
        logging.disable(logging.CRITICAL)
        with override_settings(**TEST_SETTINGS):
            return super().run_tests(*args, **kwargs)

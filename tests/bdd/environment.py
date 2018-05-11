import os

from behave import use_fixture
from django.conf import settings

from tests.bdd.behave_fixtures import browser_chrome, django_test_case, django_test_runner
from tests.bdd.steps.utils import take_screenshot

os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.bdd.settings.headless'


def before_all(context):
    context.LOG_DIR = "bdd_screenshots"


def before_scenario(context, scenario):
    use_fixture(django_test_runner, context)
    use_fixture(django_test_case, context)
    use_fixture(browser_chrome, context)

    settings.BASE_DOMAIN_NAME = context.base_url[7:]
    settings.MEDIA_URL = '//media.%s/' % settings.BASE_DOMAIN_NAME
    settings.STATIC_URL = '//static.%s/' % settings.BASE_DOMAIN_NAME
    settings.LOGIN_URL = '//%s/login/' % settings.BASE_DOMAIN_NAME


def after_step(context, step):
    if step.status == "failed":
        take_screenshot(context, step.name)

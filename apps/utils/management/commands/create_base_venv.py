import shutil
from os.path import join, exists
from django.core.management.base import BaseCommand
from django.conf import settings
from utils.sandbox import CreateVenvSandBox


class Command(BaseCommand):
    help = 'Create base venv and install base packages'

    def handle(self, *args, **options):
        if exists(settings.BASE_VENV):
            shutil.rmtree(settings.BASE_VENV, ignore_errors=False)

        res = CreateVenvSandBox().run()
        if res['exit_code'] != 0:
            raise RuntimeError(str(res))

        shutil.copytree(settings.RES_PACKAGE,
            join(settings.BASE_VENV, 'lib/python3.8/site-packages/call_me'))


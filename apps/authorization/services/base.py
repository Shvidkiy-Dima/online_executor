import shutil
from django.conf import settings
from django.db import transaction
from account.models import User


@transaction.atomic
def confirm(confirmation_email):
    if User.objects.by_email(confirmation_email.email).exists():
        return

    confirmation_email.status = confirmation_email.CONFIRMED
    user = User.objects.make_client(confirmation_email.email)
    confirmation_email.user = user
    confirmation_email.save(updae_fields=['user', 'status'])
    venv_path = make_venv(user)
    user.venv_path = venv_path
    user.save()


def make_venv(user):
    user_venv = f'{settings.VENVS_USER_DIR}/{str(user)}_venv'
    base_venv = settings.BASE_VENV
    shutil.copytree(base_venv, user_venv, symlinks=True)
    return user_venv
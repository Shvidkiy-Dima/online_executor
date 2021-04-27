from django.db import models, transaction
from django.db.models import F
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from uuid import uuid4


class UserManager(BaseUserManager):
    use_in_migrations = False

    @transaction.atomic
    def make_client(self, email, password):
        user = User(email=email)
        user.set_password(password)
        user.save()
        return user


class UserQuerySet(models.QuerySet):

    def by_email(self, email):
        return self.filter(email=email)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, db_index=True, unique=True, default=uuid4)
    username = models.CharField(max_length=124, null=True, blank=True, default=None)
    email = models.EmailField(unique=True)
    venv_path = models.FilePathField()

    objects = UserManager.from_queryset(UserQuerySet)()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f'user_{self.id}'

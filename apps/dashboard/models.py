from uuid import uuid4
from django.db import models
from django.conf import settings
from django.db.models.constraints import UniqueConstraint
from utils.models import BaseModel


class Project(BaseModel):
   # id = models.UUIDField(primary_key=True, db_index=True, unique=True, default=uuid4)
    author = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=124)

    class Meta:
        constraints = [UniqueConstraint(fields=['author_id', 'name'],
                                        name='project_name_per_user')]

    @property
    def get_non_folder_modules(self):
        return self.modules.filter(folder__isnull=True)


class Folder(BaseModel):
    name = models.CharField(max_length=124)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='folders')


class Module(BaseModel):
    id = models.UUIDField(primary_key=True, db_index=True, unique=True, default=uuid4)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='modules')
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE,
                               related_name='modules', null=True, blank=True,
                               default=None)
    code = models.BinaryField(default=b'')
    url = models.URLField()
    name = models.CharField(max_length=124)

    def save(self, *args, **kwargs):
        if self.project:
            self.url = self.generate_url()

        return super().save(*args, **kwargs)

    def generate_url(self):
        return f'{self.project.name}/{self.id}/'

    def get_url(self):
        return settings.RUN_BASE_URL + self.url

    @property
    def code_as_str(self):
        return self.code.decode('utf8')


class Package(BaseModel):
    user = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='packages')
    name = models.CharField(max_length=256)
    size = models.IntegerField()
    version = models.CharField(max_length=124, null=True, blank=True, default=None)


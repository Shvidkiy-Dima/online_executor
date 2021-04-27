from django.db import models
from django.db.models.constraints import UniqueConstraint
from utils.models import BaseModel


class Project(BaseModel):
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
        return f'{self.project.author.id}/{self.project.name}/{self.name}/'


class Package(BaseModel):
    user = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='packages')
    name = models.TextField()
    source = models.URLField()

# Generated by Django 3.2 on 2021-04-30 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='package',
            name='source',
        ),
        migrations.AddField(
            model_name='package',
            name='size',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='package',
            name='version',
            field=models.CharField(blank=True, default=None, max_length=124, null=True),
        ),
        migrations.AlterField(
            model_name='package',
            name='name',
            field=models.CharField(max_length=256),
        ),
    ]

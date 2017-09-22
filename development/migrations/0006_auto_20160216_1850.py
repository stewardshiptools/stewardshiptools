# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('development', '0005_developmentproject_cedar_comm_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='developmentproject',
            name='cedar_comm_code',
        ),
        migrations.AddField(
            model_name='developmentproject',
            name='cedar_project_code',
            field=models.CharField(max_length=80, blank=True, null=True, verbose_name='Cedar project code'),
        ),
        migrations.AddField(
            model_name='developmentproject',
            name='cedar_project_number',
            field=models.IntegerField(default=1, verbose_name='Cedar project number'),
            preserve_default=False,
        ),
    ]

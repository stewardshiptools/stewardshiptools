# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0038_remove_developmentproject_cedar_project_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='developmentgislayer',
            name='project',
            field=models.ForeignKey(blank=True, to='development.DevelopmentProject', null=True),
        ),
    ]

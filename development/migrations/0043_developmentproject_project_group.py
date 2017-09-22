# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0042_auto_20161124_1852'),
    ]

    operations = [
        migrations.AddField(
            model_name='developmentproject',
            name='project_group',
            field=models.ForeignKey(blank=True, to='development.ProjectGroup', null=True),
        ),
    ]

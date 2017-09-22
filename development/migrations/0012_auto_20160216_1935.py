# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('development', '0011_auto_20160216_1934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='developmentproject',
            name='project_tag',
            field=models.ManyToManyField(null=True, blank=True, to='development.ProjectTag'),
        ),
    ]

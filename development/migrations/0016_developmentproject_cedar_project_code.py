# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('development', '0015_auto_20160216_1955'),
    ]

    operations = [
        migrations.AddField(
            model_name='developmentproject',
            name='cedar_project_code',
            field=models.CharField(max_length=80, unique=True, verbose_name='Cedar project code', blank=True, null=True),
        ),
    ]

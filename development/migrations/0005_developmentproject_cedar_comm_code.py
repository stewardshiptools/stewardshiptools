# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('development', '0004_remove_developmentproject_cedar_comm_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='developmentproject',
            name='cedar_comm_code',
            field=models.CharField(max_length=80, verbose_name='Cedar communication code', blank=True, null=True),
        ),
    ]

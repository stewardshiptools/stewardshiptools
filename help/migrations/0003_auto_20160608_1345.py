# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('help', '0002_auto_20160608_1333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pagehelp',
            name='title',
            field=models.CharField(max_length=100, blank=True, null=True),
        ),
    ]

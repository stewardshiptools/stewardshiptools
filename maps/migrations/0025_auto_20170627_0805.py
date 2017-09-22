# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('maps', '0024_auto_20170627_0804'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='compositestyle',
            name='circle_style',
        ),
        migrations.RemoveField(
            model_name='compositestyle',
            name='polygon_style',
        ),
    ]

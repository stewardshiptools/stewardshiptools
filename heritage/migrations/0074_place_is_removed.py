# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('heritage', '0073_auto_20170501_0803'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='is_removed',
            field=models.BooleanField(default=False),
        ),
    ]

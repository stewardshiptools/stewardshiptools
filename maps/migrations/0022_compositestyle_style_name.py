# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('maps', '0021_auto_20170621_1317'),
    ]

    operations = [
        migrations.AddField(
            model_name='compositestyle',
            name='style_name',
            field=models.CharField(blank=True, null=True, max_length=50),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0043_mtkspeciesrecordline_mtkspeciesrecordpoint_mtkspeciesrecordpolygon'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='session',
            field=models.ForeignKey(to='heritage.Session', blank=True, null=True),
        ),
    ]

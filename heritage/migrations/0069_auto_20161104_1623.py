# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0068_auto_20160808_2059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='heritagegislayer',
            name='group',
            field=models.ForeignKey(to='heritage.LayerGroup', null=True, blank=True),
        ),
    ]

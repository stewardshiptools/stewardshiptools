# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0053_auto_20160614_2326'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='species',
            options={'ordering': ['description'], 'verbose_name_plural': 'species'},
        ),
        migrations.AlterField(
            model_name='mtkspeciesrecord',
            name='species',
            field=models.ForeignKey(default=1, null=True, blank=True, to='heritage.Species'),
        ),
    ]

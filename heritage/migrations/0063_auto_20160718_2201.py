# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0062_auto_20160712_2030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mtkrecord',
            name='seasons',
            field=models.ManyToManyField(to='heritage.Season', blank=True),
        ),
    ]

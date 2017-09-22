# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0006_auto_20160101_2028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='number',
            field=models.CharField(verbose_name='Session number', max_length=3),
        ),
    ]

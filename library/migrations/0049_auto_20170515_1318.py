# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('library', '0048_auto_20170515_1317'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='useandoccupancycategory',
            options={'verbose_name_plural': 'Use and Occupancy Categories'},
        ),
    ]

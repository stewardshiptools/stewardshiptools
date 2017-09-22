# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0013_harvesthistory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='harvesthistory',
            name='last_harvest',
            field=models.DateTimeField(default=datetime.datetime(2016, 10, 12, 20, 1, 19, 156241, tzinfo=utc)),
        ),
    ]

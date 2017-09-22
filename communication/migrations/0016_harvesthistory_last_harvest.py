# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0015_remove_harvesthistory_last_harvest'),
    ]

    operations = [
        migrations.AddField(
            model_name='harvesthistory',
            name='last_harvest',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]

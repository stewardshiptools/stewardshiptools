# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0014_auto_20161012_2001'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='harvesthistory',
            name='last_harvest',
        ),
    ]

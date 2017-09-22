# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('heritage', '0074_place_is_removed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='place',
            name='is_removed',
        ),
    ]

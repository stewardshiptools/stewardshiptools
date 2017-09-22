# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0009_auto_20170313_1106'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dublincore',
            name='title',
        ),
    ]

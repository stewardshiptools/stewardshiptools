# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0012_auto_20160114_2255'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='species',
            name='photo',
        ),
    ]

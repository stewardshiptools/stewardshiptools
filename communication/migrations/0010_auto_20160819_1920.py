# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('communication', '0009_auto_20160818_1358'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='communication',
            options={'ordering': ['-date']},
        ),
    ]

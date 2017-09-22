# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0017_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asset',
            name='interview',
        ),
        migrations.RemoveField(
            model_name='asset',
            name='session',
        ),
        migrations.DeleteModel(
            name='Asset',
        ),
    ]

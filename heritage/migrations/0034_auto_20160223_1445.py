# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('heritage', '0033_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sessionasset',
            name='interviewasset_ptr',
        ),
        migrations.RemoveField(
            model_name='sessionasset',
            name='session',
        ),
        migrations.DeleteModel(
            name='SessionAsset',
        ),
    ]

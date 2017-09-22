# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('assets', '0008_auto_20160616_1953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='legacy_path',
            field=models.CharField(max_length=2000, null=True, help_text='This may hold a file path pointing to the original file location',
                                   default='', blank=True),
        ),
        migrations.AlterField(
            model_name='secureasset',
            name='legacy_path',
            field=models.CharField(max_length=2000, null=True, help_text='This may hold a file path pointing to the original file location',
                                   default='', blank=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('assets', '0009_auto_20160616_1956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='legacy_path',
            field=models.CharField(help_text='This may hold a file path pointing to the original file location', blank=True, null=True,
                                   max_length=2000),
        ),
        migrations.AlterField(
            model_name='secureasset',
            name='legacy_path',
            field=models.CharField(help_text='This may hold a file path pointing to the original file location', blank=True, null=True,
                                   max_length=2000),
        ),
    ]

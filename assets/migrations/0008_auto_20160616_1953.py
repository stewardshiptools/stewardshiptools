# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('assets', '0007_auto_20160614_2247'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='legacy_path',
            field=models.CharField(blank=True, null=True, max_length=2000),
        ),
        migrations.AddField(
            model_name='secureasset',
            name='legacy_path',
            field=models.CharField(blank=True, null=True, max_length=2000),
        ),
    ]

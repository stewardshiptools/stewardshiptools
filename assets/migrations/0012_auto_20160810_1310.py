# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('assets', '0011_auto_20160715_2103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='asset_type',
            field=models.ForeignKey(to='assets.AssetType', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='secureasset',
            name='asset_type',
            field=models.ForeignKey(to='assets.AssetType', blank=True, null=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('assets', '0003_auto_20160224_2230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='name',
            field=models.CharField(max_length=100, default='FakeName'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='secureasset',
            name='name',
            field=models.CharField(max_length=100, default='FakeName'),
            preserve_default=False,
        ),
    ]

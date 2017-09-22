# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('assets', '0006_auto_20160324_1434'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='published',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='secureasset',
            name='published',
            field=models.BooleanField(default=True),
        ),
    ]

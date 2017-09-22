# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('assets', '0004_auto_20160303_1816'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='modified',
            field=models.DateTimeField(null=True, verbose_name='Date & time record modified.', auto_now=True),
        ),
        migrations.AddField(
            model_name='secureasset',
            name='modified',
            field=models.DateTimeField(null=True, verbose_name='Date & time record modified.', auto_now=True),
        ),
    ]

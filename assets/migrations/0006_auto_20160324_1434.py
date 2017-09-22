# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('assets', '0005_auto_20160321_2126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='modified',
            field=models.DateTimeField(blank=True, verbose_name='Date & time record modified.', null=True),
        ),
        migrations.AlterField(
            model_name='secureasset',
            name='modified',
            field=models.DateTimeField(blank=True, verbose_name='Date & time record modified.', null=True),
        ),
    ]

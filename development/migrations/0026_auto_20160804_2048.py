# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('development', '0025_auto_20160729_2327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='developmentproject',
            name='status',
            field=models.CharField(max_length=30, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active',
                                   verbose_name='Project status'),
        ),
    ]

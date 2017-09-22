# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('assets', '0002_auto_20160211_2003'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='comment',
            field=models.CharField(null=True, blank=True, max_length=800),
        ),
        migrations.AddField(
            model_name='secureasset',
            name='comment',
            field=models.CharField(null=True, blank=True, max_length=800),
        ),
    ]

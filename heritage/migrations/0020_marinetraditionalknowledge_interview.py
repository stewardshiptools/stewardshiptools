# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('heritage', '0019_auto_20160127_2024'),
    ]

    operations = [
        migrations.AddField(
            model_name='marinetraditionalknowledge',
            name='interview',
            field=models.ForeignKey(blank=True, null=True, to='heritage.Interview'),
        ),
    ]

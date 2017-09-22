# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('heritage', '0057_auto_20160623_1856'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='notes',
            field=models.TextField(blank=True, null=True, verbose_name='General notes on session record.'),
        ),
    ]

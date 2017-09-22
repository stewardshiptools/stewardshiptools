# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geoinfo', '0011_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='gislayermaster',
            name='layer_type',
            field=models.CharField(default='', null=True, blank=True, max_length=100),
        ),
    ]

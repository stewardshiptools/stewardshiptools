# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('maps', '0023_stylemarker_prefix'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stylecircle',
            name='radius',
            field=models.FloatField(blank=True, null=True, help_text='CircleMarker Radius: units in PIXELS. Circle Radius: units is METERS.',
                                    default=10),
        ),
    ]

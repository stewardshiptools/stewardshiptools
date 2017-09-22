# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('maps', '0025_auto_20170627_0805'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stylecircle',
            name='fill',
        ),
        migrations.RemoveField(
            model_name='stylecircle',
            name='fillColor',
        ),
        migrations.RemoveField(
            model_name='stylecircle',
            name='fillOpacity',
        ),
        migrations.RemoveField(
            model_name='stylepolyline',
            name='fill',
        ),
        migrations.RemoveField(
            model_name='stylepolyline',
            name='fillColor',
        ),
        migrations.RemoveField(
            model_name='stylepolyline',
            name='fillOpacity',
        ),
    ]

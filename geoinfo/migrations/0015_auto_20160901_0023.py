# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geoinfo', '0014_auto_20160822_2310'),
    ]

    operations = [
        migrations.AddField(
            model_name='gislayermaster',
            name='geomark',
            field=models.CharField(null=True, max_length=2083, blank=True),
        ),
        migrations.AlterField(
            model_name='gislayermaster',
            name='input_type',
            field=models.CharField(max_length=50, choices=[('wkt', 'WKT'), ('map', 'Draw on a map'), ('file', 'File'), ('geomark', 'Geomark'), ('custom', 'Custom')], default='wkt'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geoinfo', '0020_gislayermaster_wfs_geojson'),
    ]

    operations = [
        migrations.AddField(
            model_name='gislayermaster',
            name='reload_features',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='gislayermaster',
            name='input_type',
            field=models.CharField(default='wkt', max_length=50, choices=[('wkt', 'WKT'), ('map', 'Draw on a map'), ('file', 'File'), ('geomark', 'Geomark'), ('wfs', 'WFS GeoJSON'), ('custom', 'Custom')]),
        ),
        migrations.AlterField(
            model_name='gislayermaster',
            name='wfs_geojson',
            field=models.URLField(null=True, max_length=2083, blank=True, help_text='Please enter a url that resolves as WFS formatted GeoJSON', verbose_name='WFS GeoJSON'),
        ),
    ]

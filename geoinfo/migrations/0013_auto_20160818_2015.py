# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geoinfo', '0012_gislayermaster_layer_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='gislayermaster',
            name='number_of_lines',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='gislayermaster',
            name='number_of_points',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='gislayermaster',
            name='number_of_polygons',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='gislayermaster',
            name='polygons_combined_area',
            field=models.FloatField(null=True, blank=True),
        ),
    ]

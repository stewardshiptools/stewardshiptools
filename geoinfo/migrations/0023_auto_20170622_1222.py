# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('maps', '0023_stylemarker_prefix'),
        ('geoinfo', '0022_auto_20170619_1616'),
    ]

    operations = [
        migrations.AddField(
            model_name='gislayermaster',
            name='point_style',
            field=models.ForeignKey(null=True, blank=True, to='maps.StyleCircle'),
        ),
        migrations.AddField(
            model_name='gislayermaster',
            name='polygon_style',
            field=models.ForeignKey(null=True, blank=True, to='maps.StylePolygon'),
        ),
        migrations.AddField(
            model_name='gislayermaster',
            name='polyline_style',
            field=models.ForeignKey(null=True, blank=True, to='maps.StylePolyline'),
        ),
    ]

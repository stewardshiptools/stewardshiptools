# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geoinfo', '0019_auto_20170430_2303'),
    ]

    operations = [
        migrations.AddField(
            model_name='gislayermaster',
            name='wfs_geojson',
            field=models.URLField(null=True, max_length=2083, blank=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import cryptographic_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('geoinfo', '0021_auto_20170613_1439'),
    ]

    operations = [
        migrations.AddField(
            model_name='gislayermaster',
            name='wfs_password',
            field=cryptographic_fields.fields.EncryptedCharField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='gislayermaster',
            name='wfs_username',
            field=models.CharField(null=True, blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='gislayermaster',
            name='wfs_geojson',
            field=models.URLField(verbose_name='WFS GeoJSON URL', null=True, blank=True, help_text='Please enter a url that resolves as WFS formatted GeoJSON', max_length=2083),
        ),
    ]

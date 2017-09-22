# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geoinfo', '0005_auto_20160513_0502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gislayermaster',
            name='input_type',
            field=models.CharField(choices=[('wkt', 'WKT'), ('map', 'Draw on a map'), ('file', 'File'), ('custom', 'Custom')], default='wkt', max_length=50),
        ),
    ]

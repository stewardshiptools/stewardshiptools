# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geoinfo', '0016_gislayermaster_extra_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='gisfeature',
            name='image',
            field=models.ImageField(upload_to='geoinfo-images', null=True, blank=True),
        ),
    ]

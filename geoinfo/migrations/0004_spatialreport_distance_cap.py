# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geoinfo', '0003_auto_20160513_0450'),
    ]

    operations = [
        migrations.AddField(
            model_name='spatialreport',
            name='distance_cap',
            field=models.CharField(help_text='Enter a distance in meters (m) or kilometers (km).The report will only show hits that are within thisdistance.', default='5km', max_length=50),
        ),
    ]

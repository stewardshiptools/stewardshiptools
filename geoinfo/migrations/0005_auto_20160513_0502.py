# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geoinfo', '0004_spatialreport_distance_cap'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spatialreportitem',
            name='distance_cap',
            field=models.CharField(help_text='Enter a distance in meters (m) or kilometers (km).The report will only show hits that are within thisdistance.  This value overrides the value given in theoverall Spatial Report.', max_length=50, null=True, blank=True),
        ),
    ]

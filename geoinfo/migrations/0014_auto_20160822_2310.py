# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geoinfo', '0013_auto_20160818_2015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spatialreportitem',
            name='layer',
            field=models.ForeignKey(to='geoinfo.GISLayerMaster', related_name='spatialreport_items'),
        ),
    ]

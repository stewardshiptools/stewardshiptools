# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geoinfo', '0006_auto_20160524_1954'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spatialreport',
            name='report_on',
            field=models.ForeignKey(related_name='layers_reported_on', to='geoinfo.GISLayerMaster', null=True, blank=True),
        ),
    ]

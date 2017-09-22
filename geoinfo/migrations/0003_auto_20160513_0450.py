# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geoinfo', '0002_spatialreport'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpatialReportItem',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('distance_cap', models.CharField(max_length=50, help_text='Enter a distance in meters (m) or kilometers (km).The report will only show hits that are within thisdistance.  This value overrides the value given in theoverall Spatial Report.', default='5km')),
                ('layer', models.ForeignKey(to='geoinfo.GISLayerMaster')),
            ],
        ),
        migrations.RemoveField(
            model_name='spatialreport',
            name='intervals',
        ),
        migrations.RemoveField(
            model_name='spatialreport',
            name='report_against',
        ),
        migrations.AddField(
            model_name='spatialreportitem',
            name='report',
            field=models.ForeignKey(to='geoinfo.SpatialReport'),
        ),
    ]

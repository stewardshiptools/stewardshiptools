# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geoinfo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpatialReport',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('intervals', models.TextField(default='intersecting', help_text='Enter a comma or line separated list of intervals.  Intervals may either bea distance in meters (m) or kilometers (km), or else the word"intersecting".')),
                ('report_against', models.ManyToManyField(to='geoinfo.GISLayerMaster', related_name='layers_reported_against')),
                ('report_on', models.ForeignKey(to='geoinfo.GISLayerMaster', related_name='layers_reported_on')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

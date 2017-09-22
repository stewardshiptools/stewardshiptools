# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geoinfo', '0012_gislayermaster_layer_type'),
        ('heritage', '0063_auto_20160718_2201'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeritageGISLayer',
            fields=[
                ('gislayermaster_ptr', models.OneToOneField(to='geoinfo.GISLayerMaster', auto_created=True, primary_key=True, parent_link=True, serialize=False)),
                ('session', models.ForeignKey(to='heritage.Session')),
            ],
            bases=('geoinfo.gislayermaster',),
        ),
    ]

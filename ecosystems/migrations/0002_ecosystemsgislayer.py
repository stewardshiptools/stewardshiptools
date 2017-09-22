# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geoinfo', '0015_auto_20160901_0023'),
        ('ecosystems', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EcosystemsGISLayer',
            fields=[
                ('gislayermaster_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='geoinfo.GISLayerMaster')),
            ],
            bases=('geoinfo.gislayermaster',),
        ),
    ]

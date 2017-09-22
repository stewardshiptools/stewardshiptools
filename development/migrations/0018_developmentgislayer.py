# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geoinfo', '0001_initial'),
        ('development', '0017_auto_20160216_2237'),
    ]

    operations = [
        migrations.CreateModel(
            name='DevelopmentGISLayer',
            fields=[
                ('gislayermaster_ptr', models.OneToOneField(parent_link=True, to='geoinfo.GISLayerMaster', serialize=False, auto_created=True, primary_key=True)),
                ('project', models.ForeignKey(to='development.DevelopmentProject')),
            ],
            bases=('geoinfo.gislayermaster',),
        ),
    ]

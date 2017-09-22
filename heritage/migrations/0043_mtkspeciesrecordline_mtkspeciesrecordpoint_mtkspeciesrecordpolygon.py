# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0042_mtkspeciesrecord'),
    ]

    operations = [
        migrations.CreateModel(
            name='MTKSpeciesRecordLine',
            fields=[
                ('mtkspeciesrecord_ptr', models.OneToOneField(auto_created=True, serialize=False, primary_key=True, parent_link=True, to='heritage.MTKSpeciesRecord')),
                ('geometry', django.contrib.gis.db.models.fields.MultiLineStringField(srid=4326)),
            ],
            bases=('heritage.mtkspeciesrecord',),
        ),
        migrations.CreateModel(
            name='MTKSpeciesRecordPoint',
            fields=[
                ('mtkspeciesrecord_ptr', models.OneToOneField(auto_created=True, serialize=False, primary_key=True, parent_link=True, to='heritage.MTKSpeciesRecord')),
                ('geometry', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
            bases=('heritage.mtkspeciesrecord',),
        ),
        migrations.CreateModel(
            name='MTKSpeciesRecordPolygon',
            fields=[
                ('mtkspeciesrecord_ptr', models.OneToOneField(auto_created=True, serialize=False, primary_key=True, parent_link=True, to='heritage.MTKSpeciesRecord')),
                ('geometry', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
            bases=('heritage.mtkspeciesrecord',),
        ),
    ]

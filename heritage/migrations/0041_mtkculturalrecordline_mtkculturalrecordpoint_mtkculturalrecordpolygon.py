# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0040_mtkculturalrecord'),
    ]

    operations = [
        migrations.CreateModel(
            name='MTKCulturalRecordLine',
            fields=[
                ('mtkculturalrecord_ptr', models.OneToOneField(auto_created=True, parent_link=True, serialize=False, to='heritage.MTKCulturalRecord', primary_key=True)),
                ('geometry', django.contrib.gis.db.models.fields.MultiLineStringField(srid=4326)),
            ],
            bases=('heritage.mtkculturalrecord',),
        ),
        migrations.CreateModel(
            name='MTKCulturalRecordPoint',
            fields=[
                ('mtkculturalrecord_ptr', models.OneToOneField(auto_created=True, parent_link=True, serialize=False, to='heritage.MTKCulturalRecord', primary_key=True)),
                ('geometry', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
            bases=('heritage.mtkculturalrecord',),
        ),
        migrations.CreateModel(
            name='MTKCulturalRecordPolygon',
            fields=[
                ('mtkculturalrecord_ptr', models.OneToOneField(auto_created=True, parent_link=True, serialize=False, to='heritage.MTKCulturalRecord', primary_key=True)),
                ('geometry', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
            bases=('heritage.mtkculturalrecord',),
        ),
    ]

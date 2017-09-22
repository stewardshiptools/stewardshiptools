# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields
from django.conf import settings
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GISFeature',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('data', django_hstore.fields.DictionaryField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='GISLayerMaster',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('input_type', models.CharField(choices=[('wkt', 'WKT'), ('map', 'Draw on a map'), ('file', 'File')], max_length=50, default='wkt')),
                ('wkt', models.TextField(null=True, blank=True)),
                ('draw', django.contrib.gis.db.models.fields.GeometryCollectionField(null=True, blank=True, srid=4326)),
                ('file', models.FileField(null=True, blank=True, upload_to='geoinfo')),
                ('notes', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='GISFeatureLine',
            fields=[
                ('gisfeature_ptr', models.OneToOneField(parent_link=True, to='geoinfo.GISFeature', auto_created=True, serialize=False, primary_key=True)),
                ('geometry', django.contrib.gis.db.models.fields.MultiLineStringField(geography=True, srid=4326)),
            ],
            bases=('geoinfo.gisfeature',),
        ),
        migrations.CreateModel(
            name='GISFeaturePoint',
            fields=[
                ('gisfeature_ptr', models.OneToOneField(parent_link=True, to='geoinfo.GISFeature', auto_created=True, serialize=False, primary_key=True)),
                ('geometry', django.contrib.gis.db.models.fields.PointField(geography=True, srid=4326)),
            ],
            bases=('geoinfo.gisfeature',),
        ),
        migrations.CreateModel(
            name='GISFeaturePolygon',
            fields=[
                ('gisfeature_ptr', models.OneToOneField(parent_link=True, to='geoinfo.GISFeature', auto_created=True, serialize=False, primary_key=True)),
                ('geometry', django.contrib.gis.db.models.fields.MultiPolygonField(geography=True, srid=4326)),
            ],
            bases=('geoinfo.gisfeature',),
        ),
        migrations.CreateModel(
            name='GISLayer',
            fields=[
                ('gislayermaster_ptr', models.OneToOneField(parent_link=True, to='geoinfo.GISLayerMaster', auto_created=True, serialize=False, primary_key=True)),
            ],
            bases=('geoinfo.gislayermaster',),
        ),
        migrations.AddField(
            model_name='gislayermaster',
            name='author',
            field=models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='gisfeature',
            name='layer',
            field=models.ForeignKey(to='geoinfo.GISLayerMaster'),
        ),
    ]

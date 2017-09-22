# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0072_auto_20170430_2352'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='heritageasset',
            options={'verbose_name': 'Heritage File'},
        ),
        migrations.AlterModelOptions(
            name='interviewasset',
            options={'verbose_name': 'Heritage Interview File'},
        ),
        migrations.AlterModelOptions(
            name='projectasset',
            options={'verbose_name': 'Heritage Project File'},
        ),
        migrations.AlterModelOptions(
            name='sessionasset',
            options={'verbose_name': 'Heritage Session File'},
        ),
        migrations.AddField(
            model_name='place',
            name='geometry',
            field=django.contrib.gis.db.models.fields.GeometryCollectionField(srid=4326, default=None),
            preserve_default=False,
        ),
    ]

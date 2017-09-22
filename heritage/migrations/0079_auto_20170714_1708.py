# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0078_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='geometry',
            field=django.contrib.gis.db.models.fields.GeometryField(srid=4326),
        ),
    ]

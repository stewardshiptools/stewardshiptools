# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0011_leafletmap_layer_control_collapsed'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaflettilelayer',
            name='other_settings',
            field=django_hstore.fields.DictionaryField(blank=True, null=True),
        ),
    ]

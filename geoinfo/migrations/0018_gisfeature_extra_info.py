# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('geoinfo', '0017_gisfeature_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='gisfeature',
            name='extra_info',
            field=django_hstore.fields.DictionaryField(blank=True, null=True),
        ),
    ]

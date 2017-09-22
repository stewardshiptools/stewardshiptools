# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0013_auto_20160714_2151'),
    ]

    operations = [
        migrations.AddField(
            model_name='leafletmap',
            name='other_settings',
            field=django_hstore.fields.DictionaryField(blank=True, null=True),
        ),
    ]

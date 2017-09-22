# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('geoinfo', '0015_auto_20160901_0023'),
    ]

    operations = [
        migrations.AddField(
            model_name='gislayermaster',
            name='extra_info',
            field=django_hstore.fields.DictionaryField(null=True, blank=True),
        ),
    ]

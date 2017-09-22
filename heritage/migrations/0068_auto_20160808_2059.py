# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0067_heritagegislayer_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='layergroup',
            name='data',
            field=django_hstore.fields.DictionaryField(null=True, blank=True, help_text='This field is optional.'),
        ),
    ]

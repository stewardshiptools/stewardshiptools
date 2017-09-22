# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0034_developmentproject_location_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='developmentproject',
            name='misc_textareas',
            field=django_hstore.fields.DictionaryField(null=True, blank=True),
        ),
    ]

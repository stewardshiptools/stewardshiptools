# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0017_auto_20161125_1202'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='extra_info',
            field=django_hstore.fields.DictionaryField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='extra_info',
            field=django_hstore.fields.DictionaryField(blank=True, null=True),
        ),
    ]

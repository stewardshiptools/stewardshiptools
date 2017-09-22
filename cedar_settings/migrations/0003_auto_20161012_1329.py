# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_hstore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cedar_settings', '0002_auto_20161012_1948'),
    ]

    operations = [
        migrations.AddField(
            model_name='generalsetting',
            name='json_value',
            field=django_hstore.fields.DictionaryField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='generalsetting',
            name='data_type',
            field=models.CharField(default='text', max_length=200, choices=[('text', 'Text'), ('int', 'Integer'), ('float', 'Float'), ('boolean', 'Boolean'), ('date', 'Date'), ('json', 'JSON'), ('reference', 'Reference')]),
        ),
    ]

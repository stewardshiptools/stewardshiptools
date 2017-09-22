# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cedar_settings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='generalsetting',
            name='date_value',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='generalsetting',
            name='data_type',
            field=models.CharField(max_length=200, choices=[('text', 'Text'), ('int', 'Integer'), ('float', 'Float'), ('boolean', 'Boolean'), ('date', 'Date'), ('reference', 'Reference')], default='text'),
        ),
    ]

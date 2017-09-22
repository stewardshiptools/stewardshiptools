# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('development', '0023_auto_20160729_2239'),
    ]

    operations = [
        migrations.AddField(
            model_name='developmentproject',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active', max_length='30'),
        ),
    ]

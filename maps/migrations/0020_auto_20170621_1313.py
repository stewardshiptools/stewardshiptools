# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('maps', '0019_auto_20170621_1251'),
    ]

    operations = [
        migrations.AddField(
            model_name='stylecircle',
            name='style_name',
            field=models.CharField(blank=True, null=True, max_length=50),
        ),
        migrations.AddField(
            model_name='stylemarker',
            name='style_name',
            field=models.CharField(blank=True, null=True, max_length=50),
        ),
        migrations.AddField(
            model_name='stylepolygon',
            name='style_name',
            field=models.CharField(blank=True, null=True, max_length=50),
        ),
        migrations.AddField(
            model_name='stylepolyline',
            name='style_name',
            field=models.CharField(blank=True, null=True, max_length=50),
        ),
    ]

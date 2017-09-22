# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('geoinfo', '0018_gisfeature_extra_info'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gislayer',
            options={'verbose_name': 'Misc. Layer', 'verbose_name_plural': 'Misc. Layers'},
        ),
        migrations.AddField(
            model_name='gislayermaster',
            name='machine_name',
            field=models.CharField(blank=True, null=True, unique=True, max_length=200),
        ),
    ]

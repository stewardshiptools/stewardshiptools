# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0012_leaflettilelayer_other_settings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaflettilelayer',
            name='attribution',
            field=models.CharField(null=True, blank=True, max_length=500),
        ),
    ]

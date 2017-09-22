# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0047_auto_20170108_0706'),
    ]

    operations = [
        migrations.AddField(
            model_name='consultationstage',
            name='stage_weight',
            field=models.IntegerField(default=0, verbose_name='Stage weighting'),
        ),
    ]

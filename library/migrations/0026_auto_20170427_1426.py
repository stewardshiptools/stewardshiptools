# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0025_auto_20170424_1318'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='mup_category',
        ),
        migrations.AddField(
            model_name='review',
            name='mup_category',
            field=models.ManyToManyField(blank=True, to='library.MUPCategory'),
        ),
        migrations.RemoveField(
            model_name='review',
            name='use_occupancy_category',
        ),
        migrations.AddField(
            model_name='review',
            name='use_occupancy_category',
            field=models.ManyToManyField(blank=True, to='library.UseAndOccupancyCategory'),
        ),
    ]

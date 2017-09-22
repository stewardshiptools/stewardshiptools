# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0049_auto_20170515_1318'),
        ('heritage', '0075_remove_place_is_removed'),
    ]

    operations = [
        migrations.AddField(
            model_name='interview',
            name='related_items',
            field=models.ManyToManyField(blank=True, to='library.Item', related_name='related_heritage_interviews'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('maps', '0019_auto_20170621_1251'),
        ('heritage', '0076_interview_related_items'),
        ('heritage', '0077_place_add_to_community_map'),
    ]

    operations = [
        migrations.AddField(
            model_name='placetype',
            name='map_style',
            field=models.ForeignKey(null=True, blank=True, to='maps.CompositeStyle'),
        ),
    ]

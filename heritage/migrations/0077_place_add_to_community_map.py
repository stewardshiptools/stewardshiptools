# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0076_interview_related_items'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='add_to_community_map',
            field=models.BooleanField(default=False),
        ),
    ]

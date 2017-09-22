# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0048_consultationstage_stage_weight'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='consultationstage',
            options={'ordering': ['stage_weight']},
        ),
    ]

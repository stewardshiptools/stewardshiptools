# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0048_mtkrecord_interviewer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mtkrecord',
            name='participant_id',
        ),
    ]

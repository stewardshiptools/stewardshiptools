# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0051_auto_20160614_1946'),
    ]

    operations = [
        migrations.AddField(
            model_name='mtkrecord',
            name='in_transcripts',
            field=models.BooleanField(default=True),
        ),
    ]

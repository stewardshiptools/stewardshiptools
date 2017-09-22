# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0052_mtkrecord_in_transcripts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mtkrecord',
            name='participant_community',
            field=models.CharField(default='pending', max_length=100, blank=True, null=True, verbose_name='Participant community'),
        ),
    ]

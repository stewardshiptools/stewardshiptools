# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0049_remove_mtkrecord_participant_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='mtkrecord',
            name='participant_id',
            field=models.IntegerField(verbose_name='Participant ID', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mtkrecord',
            name='participant_secondary_id',
            field=models.CharField(max_length=10, verbose_name='Secondary Participant ID', blank=True, null=True),
        ),
    ]

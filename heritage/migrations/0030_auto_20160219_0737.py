# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0029_auto_20160219_0349'),
    ]

    operations = [
        migrations.RenameField(
            model_name='interview',
            old_name='interviewer',
            new_name='primary_interviewer',
        ),
        migrations.AlterField(
            model_name='interview',
            name='participant_number',
            field=models.IntegerField(verbose_name='Participant number'),
        ),
        migrations.AlterUniqueTogether(
            name='interview',
            unique_together=set([('phase', 'primary_interviewer', 'type', 'participant_number')]),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0028_auto_20160217_2338'),
    ]

    operations = [
        migrations.RenameField(
            model_name='interview',
            old_name='interview_number',
            new_name='participant_number',
        ),
        migrations.AlterUniqueTogether(
            name='interview',
            unique_together=set([('phase', 'interviewer', 'type', 'participant_number')]),
        ),
    ]

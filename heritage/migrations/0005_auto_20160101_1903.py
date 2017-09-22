# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0004_interview_interviewer_id'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='interview',
            unique_together=set([('phase', 'interviewer_id', 'type', 'interview_number')]),
        ),
    ]

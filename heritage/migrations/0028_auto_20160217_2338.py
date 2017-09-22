# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0027_interview_interviewer'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='interview',
            unique_together=set([('phase', 'interviewer', 'type', 'interview_number')]),
        ),
    ]

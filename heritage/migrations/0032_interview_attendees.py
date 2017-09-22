# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0004_auto_20160202_1146'),
        ('heritage', '0031_interview_other_interviewers'),
    ]

    operations = [
        migrations.AddField(
            model_name='interview',
            name='attendees',
            field=models.ManyToManyField(to='crm.Person', related_name='interviews_attended'),
        ),
    ]

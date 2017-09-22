# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_initial'),
        ('heritage', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='session',
            name='interviewee',
        ),
        migrations.AddField(
            model_name='interview',
            name='interviewees',
            field=models.ManyToManyField(to='crm.Person'),
        ),
    ]

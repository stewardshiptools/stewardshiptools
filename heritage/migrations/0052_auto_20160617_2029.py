# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('heritage', '0051_auto_20160617_2025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interview',
            name='attendees',
            field=models.ManyToManyField(related_name='interviews_attended', to='crm.Person', blank=True),
        ),
        migrations.AlterField(
            model_name='interview',
            name='other_interviewers',
            field=models.ManyToManyField(related_name='interviews_assisted', to='crm.Person', blank=True),
        ),
        migrations.AlterField(
            model_name='interview',
            name='participants',
            field=models.ManyToManyField(to='crm.Person', blank=True),
        ),
    ]

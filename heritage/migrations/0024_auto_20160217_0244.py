# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0023_auto_20160217_1827'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='phase_code',
            field=models.CharField(help_text='The code by which this project is referred to in the interview metadata.', null=True, blank=True, verbose_name='Phase code', unique=True, max_length=8),
        ),
        migrations.AlterField(
            model_name='project',
            name='year_text',
            field=models.CharField(help_text='The year this project took place over.', null=True, max_length=8, verbose_name='Year', blank=True),
        ),
    ]

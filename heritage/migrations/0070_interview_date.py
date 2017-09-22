# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0069_auto_20161104_1623'),
    ]

    operations = [
        migrations.AddField(
            model_name='interview',
            name='date',
            field=models.DateField(null=True, help_text='Date of the interview', verbose_name='Date', blank=True),
        ),
    ]

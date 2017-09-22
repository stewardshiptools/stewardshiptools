# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0018_auto_20160115_2002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='year_text',
            field=models.CharField(verbose_name='Year text', max_length=8, help_text='The code by which this project is referred to in the interview metadata.', unique=True),
        ),
    ]

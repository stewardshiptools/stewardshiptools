# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0003_auto_20160101_1438'),
    ]

    operations = [
        migrations.AddField(
            model_name='interview',
            name='interviewer_id',
            field=models.ForeignKey(default=1, to='heritage.InterviewerId'),
            preserve_default=False,
        ),
    ]

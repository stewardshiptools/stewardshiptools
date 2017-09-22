# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0046_auto_20160229_2006'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mtkrecord',
            name='interviewer_id',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0025_auto_20160217_0344'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='interview',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='interview',
            name='interviewer_id',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0002_auto_20160101_1436'),
    ]

    operations = [
        migrations.RenameField(
            model_name='interview',
            old_name='interviewees',
            new_name='participants',
        ),
    ]

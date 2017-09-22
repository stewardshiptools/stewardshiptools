# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('help', '0003_auto_20160608_1345'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pagehelp',
            name='title',
        ),
    ]

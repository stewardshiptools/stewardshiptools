# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0011_auto_20161012_1952'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mailbox',
            name='last_checked',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0050_auto_20170303_0807'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='developmentproject',
            name='tags',
        ),
    ]

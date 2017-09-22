# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('development', '0002_auto_20160215_2154'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='developmentproject',
            name='cedar_project_number',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('development', '0003_remove_developmentproject_cedar_project_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='developmentproject',
            name='cedar_comm_code',
        ),
    ]

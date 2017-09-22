# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0056_migrate_due_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='developmentproject',
            name='project_group',
        ),
    ]

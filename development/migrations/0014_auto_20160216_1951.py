# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('development', '0013_auto_20160216_1936'),
    ]

    operations = [
        migrations.RenameField(
            model_name='developmentproject',
            old_name='project_tag',
            new_name='tags',
        ),
    ]

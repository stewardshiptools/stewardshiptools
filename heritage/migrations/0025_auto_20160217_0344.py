# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0024_auto_20160217_0244'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='year_text',
            new_name='year_string',
        ),
    ]

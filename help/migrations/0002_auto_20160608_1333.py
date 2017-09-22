# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('help', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pagehelp',
            old_name='helptext',
            new_name='help_text',
        ),
        migrations.RenameField(
            model_name='pagehelp',
            old_name='page_id',
            new_name='page_name',
        ),
    ]

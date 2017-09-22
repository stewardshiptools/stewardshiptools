# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0027_delete_setting'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='developmentproject',
            name='external_file_no',
        ),
    ]

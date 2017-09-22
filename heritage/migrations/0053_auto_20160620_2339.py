# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0052_auto_20160617_2029'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='record',
            options={'permissions': [('view_record_meta', 'Can view meta data in records.')]},
        ),
    ]

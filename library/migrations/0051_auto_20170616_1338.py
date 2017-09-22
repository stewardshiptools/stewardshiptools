# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('library', '0050_auto_20170614_1137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='holdings',
            name='digital_file_name',
            field=models.CharField(max_length=2000, blank=True, null=True),
        ),
    ]

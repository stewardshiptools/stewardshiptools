# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0011_projectasset'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interviewasset',
            name='secureasset_ptr',
        ),
        migrations.AddField(
            model_name='interviewasset',
            name='projectasset_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, to='heritage.ProjectAsset', default=1, serialize=False),
            preserve_default=False,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('heritage', '0034_auto_20160223_1445'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='interviewasset',
            name='projectasset_ptr',
        ),
        migrations.AddField(
            model_name='interviewasset',
            name='heritageasset_ptr',
            field=models.OneToOneField(to='heritage.HeritageAsset', default=1, serialize=False, auto_created=True, parent_link=True,
                                       primary_key=True),
            preserve_default=False,
        ),
    ]

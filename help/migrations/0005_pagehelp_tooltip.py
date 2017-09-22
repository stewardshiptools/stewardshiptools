# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('help', '0004_remove_pagehelp_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagehelp',
            name='tooltip',
            field=models.CharField(default='Help', max_length=50),
        ),
    ]

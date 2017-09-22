# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0051_auto_20170616_1338'),
    ]

    operations = [
        migrations.AddField(
            model_name='holdings',
            name='dimensions',
            field=models.CharField(max_length=250, blank=True, null=True, help_text='If the Item is a physical object, add  dimensions. Example 10 cm x 20 cm x 3 cm'),
        ),
    ]

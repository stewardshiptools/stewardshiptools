# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('library', '0046_auto_20170512_1505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='holdings',
            name='item_type_comments',
            field=models.TextField(blank=True, null=True, help_text='The Item Type is selected in the Identification'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0021_auto_20170424_1308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemtype',
            name='belongs_to',
            field=models.CharField(max_length=100, blank=True, null=True, verbose_name='App that this object belongs to'),
        ),
    ]

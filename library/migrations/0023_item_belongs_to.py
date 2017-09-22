# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0022_auto_20170424_1313'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='belongs_to',
            field=models.CharField(null=True, blank=True, max_length=100, verbose_name='App that this object belongs to'),
        ),
    ]

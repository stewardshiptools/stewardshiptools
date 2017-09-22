# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0033_auto_20161013_2237'),
    ]

    operations = [
        migrations.AddField(
            model_name='developmentproject',
            name='location_description',
            field=models.TextField(blank=True, help_text="Short description of the project's location.", verbose_name='Location Description'),
        ),
    ]

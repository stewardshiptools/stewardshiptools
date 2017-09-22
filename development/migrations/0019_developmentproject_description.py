# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('development', '0018_developmentgislayer'),
        ('development', '0018_developmentasset_developmentprojectasset'),
    ]

    operations = [
        migrations.AddField(
            model_name='developmentproject',
            name='description',
            field=models.TextField(verbose_name='Description', blank=True, help_text='Short description of project/permit.'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sanitizer', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relatedsensitivephrase',
            name='replace_phrase',
            field=models.CharField(max_length=200, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='sensitivephrase',
            name='replace_phrase',
            field=models.CharField(max_length=200, blank=True, null=True),
        ),
    ]

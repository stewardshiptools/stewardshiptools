# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sanitizer', '0002_auto_20160622_2129'),
    ]

    operations = [
        migrations.AddField(
            model_name='relatedsensitivephrase',
            name='check_for_word_boundary_end',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='relatedsensitivephrase',
            name='check_for_word_boundary_start',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='sensitivephrase',
            name='check_for_word_boundary_end',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='sensitivephrase',
            name='check_for_word_boundary_start',
            field=models.BooleanField(default=True),
        ),
    ]

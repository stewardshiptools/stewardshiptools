# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0050_auto_20160301_0030'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recordsessionlink',
            options={'ordering': ['session__date', 'record__name']},
        ),
        migrations.AlterModelOptions(
            name='speciesgroup',
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='mtkrecord',
            name='in_gdb',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='record',
            name='published',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='phase_code',
            field=models.CharField(null=True, unique=True, help_text='Project phase code.', verbose_name='Phase code', max_length=8, blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='year_string',
            field=models.CharField(null=True, verbose_name='Year', blank=True, help_text='The year this project took place.', max_length=8),
        ),
    ]

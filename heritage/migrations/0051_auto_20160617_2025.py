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
            name='species',
            options={'verbose_name_plural': 'species', 'ordering': ['description']},
        ),
        migrations.AlterField(
            model_name='project',
            name='phase_code',
            field=models.CharField(max_length=8, null=True, help_text='Project phase code.', blank=True, verbose_name='Phase code', unique=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='year_string',
            field=models.CharField(help_text='The year this project took place.', null=True, verbose_name='Year', blank=True, max_length=8),
        ),
        migrations.AlterField(
            model_name='session',
            name='audio_files',
            field=models.CharField(max_length=200, verbose_name='Audio files', blank=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='duration',
            field=models.CharField(max_length=7, verbose_name='Duration', blank=True),
        ),
        migrations.AlterField(
            model_name='session',
            name='transcript_file',
            field=models.CharField(max_length=15, verbose_name='Transcript file', blank=True,
                                   choices=[('trans1', 'trans1'), ('trans2', 'trans2'), ('trans3', 'trans3'), ('trans4', 'trans4'),
                                            ('trans5', 'trans5'), ('trans6', 'trans6'), ('trans7', 'trans7'), ('trans8', 'trans8'),
                                            ('trans5', 'trans5'), ('trans6', 'trans6'), ('trans7', 'trans7'), ('trans8', 'trans8'),
                                            ('trans9', 'trans9'), ('trans10', 'trans10'), ('trans11', 'trans11')]),
        ),
        migrations.AlterField(
            model_name='session',
            name='video_files',
            field=models.CharField(max_length=200, verbose_name='Video files', blank=True),
        ),
    ]

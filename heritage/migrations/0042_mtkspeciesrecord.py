# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0041_mtkculturalrecordline_mtkculturalrecordpoint_mtkculturalrecordpolygon'),
    ]

    operations = [
        migrations.CreateModel(
            name='MTKSpeciesRecord',
            fields=[
                ('mtkrecord_ptr', models.OneToOneField(auto_created=True, parent_link=True, to='heritage.MTKRecord', serialize=False, primary_key=True)),
                ('species_inferred', models.BooleanField(default=False)),
                ('species_other_detail', models.CharField(help_text='If value feature coded as "other", what was written in?', max_length=30, blank=True, verbose_name='Species other detail')),
                ('fishing_method_inferred', models.BooleanField(default=False, verbose_name='Fishing method inferred?')),
                ('fishing_method_other_detail', models.CharField(help_text='If value feature coded as "other", what was written in?', max_length=30, blank=True, verbose_name='Fishing method other detail')),
                ('ecological_value_inferred', models.BooleanField(default=False, verbose_name='Ecological value inferred?')),
                ('temporal_trend_inferred', models.BooleanField(default=False, verbose_name='Temporal trend inferred?')),
                ('temporal_trend_comment', models.TextField(blank=True, verbose_name='Temporal trend comment')),
                ('f34', models.CharField(null=True, max_length=200, blank=True, verbose_name='F34')),
                ('ecological_observation_only', models.NullBooleanField(default=False, verbose_name='Ecological observation only?')),
                ('ecological_value', models.ForeignKey(null=True, to='heritage.EcologicalValue', blank=True)),
                ('fishing_method', models.ForeignKey(null=True, to='heritage.FishingMethod', blank=True)),
                ('species', models.ForeignKey(to='heritage.Species', default=1)),
                ('species_theme', models.ForeignKey(null=True, to='heritage.SpeciesTheme', blank=True)),
                ('temporal_trend', models.ForeignKey(null=True, to='heritage.TemporalTrend', blank=True)),
            ],
            bases=('heritage.mtkrecord',),
        ),
    ]

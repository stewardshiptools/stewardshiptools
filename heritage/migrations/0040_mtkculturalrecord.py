# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0039_mtkrecord'),
    ]

    operations = [
        migrations.CreateModel(
            name='MTKCulturalRecord',
            fields=[
                ('mtkrecord_ptr', models.OneToOneField(primary_key=True, to='heritage.MTKRecord', auto_created=True, parent_link=True, serialize=False)),
                ('ecological_feature_other_detail', models.CharField(verbose_name='Ecological feature other detail', blank=True, help_text='If ecological feature coded as "other", what was written in?', max_length=30)),
                ('ecological_feature_inferred', models.BooleanField(default=False)),
                ('cultural_feature_other_detail', models.CharField(verbose_name='Cultural feature other detail', blank=True, help_text='If cultural feature coded as "other", what was written in?', max_length=30)),
                ('cultural_feature_inferred', models.BooleanField(default=False)),
                ('industrial_feature_other_detail', models.CharField(verbose_name='Industrial feature other detail', blank=True, help_text='If cultural feature coded as "other", what was written in?', max_length=30)),
                ('industrial_feature_inferred', models.BooleanField(default=False)),
                ('management_feature_other_detail', models.CharField(verbose_name='Management feature other detail', blank=True, help_text='If management feature coded as "other", what was written in?', max_length=30)),
                ('management_feature_inferred', models.BooleanField(default=False)),
                ('value_feature_other_detail', models.CharField(verbose_name='Value feature other detail', blank=True, help_text='If value feature coded as "other", what was written in?', max_length=30)),
                ('value_feature_inferred', models.BooleanField(default=False)),
                ('travel_mode_inferred', models.BooleanField(default=False, verbose_name='Travel Mode inferred?')),
                ('target_species_inferred', models.BooleanField(default=False, verbose_name='Target species inferred?')),
                ('target_species_other_detail', models.CharField(verbose_name='Target species other detail', blank=True, help_text='If target species coded as "other", what was written in?', max_length=30)),
                ('secondary_species_inferred', models.BooleanField(default=False, verbose_name='Secondary species inferred?')),
                ('secondary_species_other_detail', models.CharField(verbose_name='Secondary species other detail', blank=True, help_text='If secondary species coded as "other", what was written in?', max_length=30)),
                ('cultural_feature', models.ForeignKey(null=True, blank=True, to='heritage.Feature', related_name='cultural')),
                ('ecological_feature', models.ForeignKey(null=True, blank=True, to='heritage.Feature', related_name='ecological')),
                ('group', models.ForeignKey(default=1, to='heritage.Group')),
                ('industrial_feature', models.ForeignKey(null=True, blank=True, to='heritage.Feature', related_name='industrial')),
                ('management_feature', models.ForeignKey(null=True, blank=True, to='heritage.Feature', related_name='management')),
                ('secondary_species', models.ForeignKey(null=True, blank=True, to='heritage.Species', related_name='secondary')),
                ('target_species', models.ForeignKey(null=True, blank=True, to='heritage.Species', related_name='target')),
                ('travel_mode', models.ForeignKey(null=True, blank=True, to='heritage.TravelMode')),
                ('value_feature', models.ForeignKey(null=True, blank=True, to='heritage.Feature', related_name='value')),
            ],
            bases=('heritage.mtkrecord',),
        ),
    ]

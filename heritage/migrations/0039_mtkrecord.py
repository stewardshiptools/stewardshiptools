# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0038_record'),
    ]

    operations = [
        migrations.CreateModel(
            name='MTKRecord',
            fields=[
                ('record_ptr', models.OneToOneField(to='heritage.Record', auto_created=True, serialize=False, primary_key=True, parent_link=True)),
                ('map_feature', models.CharField(max_length=10, blank=True, verbose_name='Map feature')),
                ('link_code', models.CharField(max_length=25, blank=True, verbose_name='Link code')),
                ('verification_required', models.BooleanField(verbose_name='Verification required?', default=False)),
                ('interview_number', models.IntegerField(blank=True, null=True, verbose_name='Interview number')),
                ('comments', models.TextField(blank=True, verbose_name='Comments')),
                ('shape_type_inferred', models.BooleanField(verbose_name='Shape type inferred?', default=False)),
                ('base_map', models.CharField(max_length=30, blank=True, null=True, verbose_name='Base map')),
                ('scan', models.IntegerField(verbose_name='Scan', default=0)),
                ('data_source_inferred', models.BooleanField(default=False)),
                ('gazetted_place_name', models.CharField(max_length=200, blank=True, verbose_name='Gazetted place name')),
                ('local_place_name', models.CharField(max_length=200, blank=True, verbose_name='Local place name')),
                ('first_nations_place_name', models.CharField(max_length=200, blank=True, verbose_name='First Nations place name')),
                ('linguistic_group_inferred', models.BooleanField(verbose_name='Linguistic group inferred?', default=False)),
                ('season_inferred', models.BooleanField(default=False)),
                ('use_other_detail', models.CharField(max_length=30, blank=True, help_text='If use coded as "other", what was written in?', verbose_name='Use other detail')),
                ('use_inferred', models.BooleanField(verbose_name='Use inferred?', default=False)),
                ('time_frame_start_inferred', models.BooleanField(verbose_name='Time frame inferred?', default=False)),
                ('time_frame_end_inferred', models.BooleanField(verbose_name='Time frame inferred?', default=False)),
                ('time_frame_comments', models.TextField(blank=True, verbose_name='Time frame comments')),
                ('quotes', models.TextField(blank=True, verbose_name='Quotes')),
                ('comments_2', models.TextField(blank=True, verbose_name='Comments')),
                ('related_documents', models.CharField(max_length=200, blank=True, verbose_name='Related documents')),
                ('notes_for_map', models.CharField(max_length=200, blank=True, verbose_name='Notes for map')),
                ('checked_by_kb', models.CharField(max_length=300, blank=True, verbose_name='Checked by KB')),
                ('participant_community', models.CharField(max_length=100, verbose_name='Participant community', default='pending')),
                ('accuracy', models.ForeignKey(blank=True, to='heritage.Accuracy', null=True)),
                ('data_entry_id', models.ForeignKey(to='heritage.DataEntryId', default=1)),
                ('data_source', models.ForeignKey(blank=True, to='heritage.DataSource', null=True)),
                ('harvest_method', models.ForeignKey(help_text='Harvest method/observation type', blank=True, to='heritage.HarvestMethod', null=True)),
                ('info_type', models.ForeignKey(to='heritage.InfoType', default=1)),
                ('interview', models.ForeignKey(blank=True, to='heritage.Interview', null=True)),
                ('interviewer_id', models.ForeignKey(blank=True, to='heritage.InterviewerId', null=True)),
                ('linguistic_group', models.ForeignKey(blank=True, to='heritage.LinguisticGroup', null=True)),
                ('participant_id', models.ForeignKey(blank=True, to='heritage.ParticipantId', null=True)),
                ('project', models.ForeignKey(to='heritage.Project', default=1)),
                ('seasons', models.ManyToManyField(to='heritage.Season')),
                ('shape_type', models.ForeignKey(blank=True, to='heritage.ShapeType', null=True)),
                ('time_frame_end', models.ForeignKey(related_name='ends', blank=True, to='heritage.TimeFrame', null=True)),
                ('time_frame_start', models.ForeignKey(related_name='starts', blank=True, to='heritage.TimeFrame', null=True)),
                ('use', models.ForeignKey(blank=True, to='heritage.Use', null=True)),
            ],
            bases=('heritage.record',),
        ),
    ]

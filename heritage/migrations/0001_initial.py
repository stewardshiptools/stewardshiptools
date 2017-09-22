# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Accuracy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('description', models.CharField(verbose_name='Description', max_length=50)),
                ('database_code', models.CharField(verbose_name='Database code', max_length=1, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='DataEntryId',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('data_entry_id', models.CharField(verbose_name='Data entry ID', null=True, max_length=10, blank=True)),
                ('person', models.ForeignKey(null=True, to='crm.Person', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='DataSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('description', models.CharField(verbose_name='Description', max_length=30)),
                ('database_code', models.CharField(verbose_name='Database code', max_length=2, unique=True)),
                ('comments', models.CharField(verbose_name='Comments', blank=True, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='EcologicalValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('description', models.CharField(verbose_name='Description', max_length=100)),
                ('database_code', models.CharField(verbose_name='Database code', max_length=5, unique=True)),
                ('comments', models.CharField(verbose_name='Comments', blank=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('description', models.CharField(verbose_name='Description', max_length=100)),
                ('database_code', models.CharField(verbose_name='Database code', max_length=5, unique=True)),
                ('comments', models.CharField(verbose_name='Comments', blank=True, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='FeatureGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='Name', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='FishingMethod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('description', models.CharField(verbose_name='Description', max_length=100)),
                ('database_code', models.CharField(verbose_name='Database code', max_length=5, unique=True)),
                ('comments', models.CharField(verbose_name='Comments', blank=True, max_length=100)),
                ('inferred', models.BooleanField(verbose_name='Inferred?', default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name', null=True, default='pending', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='HarvestMethod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='Name', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='InfoType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('description', models.CharField(verbose_name='Description', max_length=50)),
                ('database_code', models.CharField(verbose_name='Database code', max_length=1, unique=True)),
                ('comments', models.CharField(verbose_name='Comments', blank=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Interview',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('interview_number', models.IntegerField(verbose_name='Interview number')),
                ('community', models.CharField(verbose_name='Community', max_length=300)),
                ('type', models.CharField(max_length=5, choices=[('video', 'Video'), ('audio', 'Audio')])),
            ],
        ),
        migrations.CreateModel(
            name='InterviewerId',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('interviewer_id', models.CharField(verbose_name='Interviewer ID', max_length=10)),
                ('person', models.ForeignKey(null=True, to='crm.Person', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='LinguisticGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('description', models.CharField(verbose_name='Description', max_length=100)),
                ('database_code', models.CharField(verbose_name='Database code', max_length=4, unique=True)),
                ('comments', models.CharField(verbose_name='Comments', blank=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='MarineTraditionalKnowledge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('map_feature', models.CharField(verbose_name='Map feature', blank=True, max_length=10)),
                ('link_code', models.CharField(verbose_name='Link code', blank=True, max_length=25)),
                ('verification_required', models.BooleanField(verbose_name='Verification required?', default=False)),
                ('interview_number', models.IntegerField(verbose_name='Interview number', null=True, blank=True)),
                ('comments', models.TextField(verbose_name='Comments', blank=True)),
                ('shape_type_inferred', models.BooleanField(verbose_name='Shape type inferred?', default=False)),
                ('base_map', models.CharField(verbose_name='Base map', null=True, max_length=30, blank=True)),
                ('scan', models.IntegerField(verbose_name='Scan', default=0)),
                ('data_source_inferred', models.BooleanField(default=False)),
                ('gazetted_place_name', models.CharField(verbose_name='Gazetted place name', blank=True, max_length=200)),
                ('local_place_name', models.CharField(verbose_name='Local place name', blank=True, max_length=200)),
                ('first_nations_place_name', models.CharField(verbose_name='First Nations place name', blank=True, max_length=200)),
                ('linguistic_group_inferred', models.BooleanField(verbose_name='Linguistic group inferred?', default=False)),
                ('season_inferred', models.BooleanField(default=False)),
                ('use_other_detail', models.CharField(verbose_name='Use other detail', blank=True, help_text='If use coded as "other", what was written in?', max_length=30)),
                ('use_inferred', models.BooleanField(verbose_name='Use inferred?', default=False)),
                ('time_frame_start_inferred', models.BooleanField(verbose_name='Time frame inferred?', default=False)),
                ('time_frame_end_inferred', models.BooleanField(verbose_name='Time frame inferred?', default=False)),
                ('time_frame_comments', models.TextField(verbose_name='Time frame comments', blank=True)),
                ('quotes', models.TextField(verbose_name='Quotes', blank=True)),
                ('comments_2', models.TextField(verbose_name='Comments', blank=True)),
                ('related_documents', models.CharField(verbose_name='Related documents', blank=True, max_length=200)),
                ('notes_for_map', models.CharField(verbose_name='Notes for map', blank=True, max_length=200)),
                ('checked_by_kb', models.CharField(verbose_name='Checked by KB', blank=True, max_length=300)),
                ('participant_community', models.CharField(verbose_name='Participant community', default='pending', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ParticipantId',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('participant_id', models.IntegerField(verbose_name='Participant ID', default=0)),
                ('participant_secondary_id', models.CharField(verbose_name='Participant secondary ID', blank=True, max_length=2, choices=[('a', 'a'), ('b', 'b'), ('ab', 'ab'), ('c', 'c')])),
                ('person', models.ForeignKey(null=True, to='crm.Person', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='Name', max_length=100)),
                ('year_text', models.CharField(verbose_name='Phase code', help_text='The code by which this project is referred to in the interview metadata.', max_length=8)),
                ('start_date', models.DateField(verbose_name='Start date', null=True, blank=True)),
                ('end_date', models.DateField(verbose_name='End date', null=True, blank=True)),
                ('location', models.CharField(verbose_name='Location', blank=True, max_length=300)),
                ('background', models.TextField(verbose_name='Background', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('description', models.CharField(verbose_name='Description', max_length=100)),
                ('database_code', models.CharField(verbose_name='Database code', max_length=4, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('number', models.IntegerField(verbose_name='Session number')),
                ('date', models.DateField(verbose_name='Date', null=True, help_text='Date on which the interview session occurred.', blank=True)),
                ('transcript_file', models.CharField(verbose_name='Transcript file', max_length=15, choices=[('trans1', 'trans1'), ('trans2', 'trans2'), ('trans3', 'trans3'), ('trans4', 'trans4'), ('trans5', 'trans5'), ('trans6', 'trans6'), ('trans7', 'trans7'), ('trans8', 'trans8'), ('trans5', 'trans5'), ('trans6', 'trans6'), ('trans7', 'trans7'), ('trans8', 'trans8'), ('trans9', 'trans9'), ('trans10', 'trans10'), ('trans11', 'trans11')])),
                ('duration', models.CharField(verbose_name='Duration', max_length=7)),
                ('audio_file_code', models.CharField(verbose_name='Audio file code', blank=True, max_length=40)),
                ('audio_files', models.CharField(verbose_name='Audio files', max_length=200)),
                ('video_files', models.CharField(verbose_name='Video files', max_length=200)),
                ('transcription_file_code', models.CharField(verbose_name='Audio file code', blank=True, max_length=24)),
                ('checked_by_interviewer', models.CharField(verbose_name='Checked by interviewer', blank=True, max_length=15)),
                ('corrected_by_jw', models.NullBooleanField(verbose_name='Corrected by JW', max_length=3)),
                ('sent_for_archiving', models.DateField(verbose_name='Sent for archiving', null=True, blank=True)),
                ('copy_given_to_participant', models.DateField(verbose_name='Copy given to participant', null=True, blank=True)),
                ('janet_notes', models.TextField(verbose_name='Janet notes', blank=True)),
                ('notes_on_files', models.TextField(verbose_name='Notes on files', blank=True)),
                ('other_media', models.TextField(verbose_name='Other media', blank=True)),
                ('missing', models.TextField(verbose_name='Missing', blank=True)),
                ('final_transcript_from_janet', models.NullBooleanField(verbose_name='Final transcript from Janet?')),
                ('interview', models.ForeignKey(to='heritage.Interview')),
                ('interviewee', models.ManyToManyField(to='crm.Person')),
            ],
        ),
        migrations.CreateModel(
            name='ShapeType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('description', models.CharField(verbose_name='Description', max_length=30)),
                ('database_code', models.CharField(verbose_name='Database code', max_length=5, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Species',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('description', models.CharField(verbose_name='Description', max_length=100)),
                ('database_code', models.CharField(verbose_name='Database code', max_length=5, unique=True)),
                ('other_detail', models.CharField(verbose_name='Other detail', blank=True, help_text='If coded as "other", what was written in?', max_length=30)),
                ('name_equivalents', models.CharField(verbose_name='Name equivalents', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SpeciesGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='Name', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='SpeciesTheme',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='Name', null=True, max_length=100, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='TemporalTrend',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('description', models.CharField(verbose_name='Description', max_length=100)),
                ('database_code', models.CharField(verbose_name='Database code', max_length=4, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='TimeFrame',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('description', models.CharField(verbose_name='Description', max_length=100)),
                ('database_code', models.CharField(verbose_name='Database code', max_length=4, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='TravelMode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('description', models.CharField(verbose_name='Description', max_length=100)),
                ('database_code', models.CharField(verbose_name='Database code', max_length=4, unique=True)),
                ('inferred', models.BooleanField(verbose_name='Inferred?', default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Use',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('description', models.CharField(verbose_name='Description', max_length=100)),
                ('database_code', models.CharField(verbose_name='Database code', max_length=4, unique=True)),
                ('comments', models.CharField(verbose_name='Comments', blank=True, max_length=100)),
                ('inferred', models.BooleanField(verbose_name='Inferred?', default=False)),
            ],
        ),
        migrations.CreateModel(
            name='CulturalObservation',
            fields=[
                ('marinetraditionalknowledge_ptr', models.OneToOneField(parent_link=True, serialize=False, auto_created=True, to='heritage.MarineTraditionalKnowledge', primary_key=True)),
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
                ('travel_mode_inferred', models.BooleanField(verbose_name='Travel Mode inferred?', default=False)),
                ('target_species_inferred', models.BooleanField(verbose_name='Target species inferred?', default=False)),
                ('target_species_other_detail', models.CharField(verbose_name='Target species other detail', blank=True, help_text='If target species coded as "other", what was written in?', max_length=30)),
                ('secondary_species_inferred', models.BooleanField(verbose_name='Secondary species inferred?', default=False)),
                ('secondary_species_other_detail', models.CharField(verbose_name='Secondary species other detail', blank=True, help_text='If secondary species coded as "other", what was written in?', max_length=30)),
            ],
            bases=('heritage.marinetraditionalknowledge',),
        ),
        migrations.CreateModel(
            name='SpeciesObservation',
            fields=[
                ('marinetraditionalknowledge_ptr', models.OneToOneField(parent_link=True, serialize=False, auto_created=True, to='heritage.MarineTraditionalKnowledge', primary_key=True)),
                ('species_inferred', models.BooleanField(default=False)),
                ('species_other_detail', models.CharField(verbose_name='Species other detail', blank=True, help_text='If value feature coded as "other", what was written in?', max_length=30)),
                ('fishing_method_inferred', models.BooleanField(verbose_name='Fishing method inferred?', default=False)),
                ('fishing_method_other_detail', models.CharField(verbose_name='Fishing method other detail', blank=True, help_text='If value feature coded as "other", what was written in?', max_length=30)),
                ('ecological_value_inferred', models.BooleanField(verbose_name='Ecological value inferred?', default=False)),
                ('temporal_trend_inferred', models.BooleanField(verbose_name='Temporal trend inferred?', default=False)),
                ('temporal_trend_comment', models.TextField(verbose_name='Temporal trend comment', blank=True)),
                ('f34', models.CharField(verbose_name='F34', null=True, max_length=200, blank=True)),
                ('ecological_observation_only', models.NullBooleanField(verbose_name='Ecological observation only?', default=False)),
            ],
            bases=('heritage.marinetraditionalknowledge',),
        ),
        migrations.AddField(
            model_name='species',
            name='species_group',
            field=models.ForeignKey(default=1, to='heritage.SpeciesGroup'),
        ),
        migrations.AddField(
            model_name='marinetraditionalknowledge',
            name='accuracy',
            field=models.ForeignKey(null=True, to='heritage.Accuracy', blank=True),
        ),
        migrations.AddField(
            model_name='marinetraditionalknowledge',
            name='data_entry_id',
            field=models.ForeignKey(default=1, to='heritage.DataEntryId'),
        ),
        migrations.AddField(
            model_name='marinetraditionalknowledge',
            name='data_source',
            field=models.ForeignKey(null=True, to='heritage.DataSource', blank=True),
        ),
        migrations.AddField(
            model_name='marinetraditionalknowledge',
            name='harvest_method',
            field=models.ForeignKey(null=True, help_text='Harvest method/observation type', blank=True, to='heritage.HarvestMethod'),
        ),
        migrations.AddField(
            model_name='marinetraditionalknowledge',
            name='info_type',
            field=models.ForeignKey(default=1, to='heritage.InfoType'),
        ),
        migrations.AddField(
            model_name='marinetraditionalknowledge',
            name='interviewer_id',
            field=models.ForeignKey(null=True, to='heritage.InterviewerId', blank=True),
        ),
        migrations.AddField(
            model_name='marinetraditionalknowledge',
            name='linguistic_group',
            field=models.ForeignKey(null=True, to='heritage.LinguisticGroup', blank=True),
        ),
        migrations.AddField(
            model_name='marinetraditionalknowledge',
            name='participant_id',
            field=models.ForeignKey(null=True, to='heritage.ParticipantId', blank=True),
        ),
        migrations.AddField(
            model_name='marinetraditionalknowledge',
            name='project',
            field=models.ForeignKey(default=1, to='heritage.Project'),
        ),
        migrations.AddField(
            model_name='marinetraditionalknowledge',
            name='seasons',
            field=models.ManyToManyField(to='heritage.Season'),
        ),
        migrations.AddField(
            model_name='marinetraditionalknowledge',
            name='shape_type',
            field=models.ForeignKey(null=True, to='heritage.ShapeType', blank=True),
        ),
        migrations.AddField(
            model_name='marinetraditionalknowledge',
            name='time_frame_end',
            field=models.ForeignKey(null=True, to='heritage.TimeFrame', related_name='ends', blank=True),
        ),
        migrations.AddField(
            model_name='marinetraditionalknowledge',
            name='time_frame_start',
            field=models.ForeignKey(null=True, to='heritage.TimeFrame', related_name='starts', blank=True),
        ),
        migrations.AddField(
            model_name='marinetraditionalknowledge',
            name='use',
            field=models.ForeignKey(null=True, to='heritage.Use', blank=True),
        ),
        migrations.AddField(
            model_name='interview',
            name='phase',
            field=models.ForeignKey(to='heritage.Project'),
        ),
        migrations.AddField(
            model_name='feature',
            name='feature_group',
            field=models.ForeignKey(default=1, to='heritage.FeatureGroup'),
        ),
        migrations.CreateModel(
            name='CulturalObservationLine',
            fields=[
                ('culturalobservation_ptr', models.OneToOneField(parent_link=True, serialize=False, auto_created=True, to='heritage.CulturalObservation', primary_key=True)),
                ('geometry', django.contrib.gis.db.models.fields.MultiLineStringField(srid=4326)),
            ],
            bases=('heritage.culturalobservation',),
        ),
        migrations.CreateModel(
            name='CulturalObservationPoint',
            fields=[
                ('culturalobservation_ptr', models.OneToOneField(parent_link=True, serialize=False, auto_created=True, to='heritage.CulturalObservation', primary_key=True)),
                ('geometry', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
            bases=('heritage.culturalobservation',),
        ),
        migrations.CreateModel(
            name='CulturalObservationPolygon',
            fields=[
                ('culturalobservation_ptr', models.OneToOneField(parent_link=True, serialize=False, auto_created=True, to='heritage.CulturalObservation', primary_key=True)),
                ('geometry', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
            bases=('heritage.culturalobservation',),
        ),
        migrations.CreateModel(
            name='SpeciesObservationLine',
            fields=[
                ('speciesobservation_ptr', models.OneToOneField(parent_link=True, serialize=False, auto_created=True, to='heritage.SpeciesObservation', primary_key=True)),
                ('geometry', django.contrib.gis.db.models.fields.MultiLineStringField(srid=4326)),
            ],
            bases=('heritage.speciesobservation',),
        ),
        migrations.CreateModel(
            name='SpeciesObservationPoint',
            fields=[
                ('speciesobservation_ptr', models.OneToOneField(parent_link=True, serialize=False, auto_created=True, to='heritage.SpeciesObservation', primary_key=True)),
                ('geometry', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
            bases=('heritage.speciesobservation',),
        ),
        migrations.CreateModel(
            name='SpeciesObservationPolygon',
            fields=[
                ('speciesobservation_ptr', models.OneToOneField(parent_link=True, serialize=False, auto_created=True, to='heritage.SpeciesObservation', primary_key=True)),
                ('geometry', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
            ],
            bases=('heritage.speciesobservation',),
        ),
        migrations.AddField(
            model_name='speciesobservation',
            name='ecological_value',
            field=models.ForeignKey(null=True, to='heritage.EcologicalValue', blank=True),
        ),
        migrations.AddField(
            model_name='speciesobservation',
            name='fishing_method',
            field=models.ForeignKey(null=True, to='heritage.FishingMethod', blank=True),
        ),
        migrations.AddField(
            model_name='speciesobservation',
            name='species',
            field=models.ForeignKey(default=1, to='heritage.Species'),
        ),
        migrations.AddField(
            model_name='speciesobservation',
            name='species_theme',
            field=models.ForeignKey(null=True, to='heritage.SpeciesTheme', blank=True),
        ),
        migrations.AddField(
            model_name='speciesobservation',
            name='temporal_trend',
            field=models.ForeignKey(null=True, to='heritage.TemporalTrend', blank=True),
        ),
        migrations.AddField(
            model_name='culturalobservation',
            name='cultural_feature',
            field=models.ForeignKey(null=True, to='heritage.Feature', related_name='cultural', blank=True),
        ),
        migrations.AddField(
            model_name='culturalobservation',
            name='ecological_feature',
            field=models.ForeignKey(null=True, to='heritage.Feature', related_name='ecological', blank=True),
        ),
        migrations.AddField(
            model_name='culturalobservation',
            name='group',
            field=models.ForeignKey(default=1, to='heritage.Group'),
        ),
        migrations.AddField(
            model_name='culturalobservation',
            name='industrial_feature',
            field=models.ForeignKey(null=True, to='heritage.Feature', related_name='industrial', blank=True),
        ),
        migrations.AddField(
            model_name='culturalobservation',
            name='management_feature',
            field=models.ForeignKey(null=True, to='heritage.Feature', related_name='management', blank=True),
        ),
        migrations.AddField(
            model_name='culturalobservation',
            name='secondary_species',
            field=models.ForeignKey(null=True, to='heritage.Species', related_name='secondary', blank=True),
        ),
        migrations.AddField(
            model_name='culturalobservation',
            name='target_species',
            field=models.ForeignKey(null=True, to='heritage.Species', related_name='target', blank=True),
        ),
        migrations.AddField(
            model_name='culturalobservation',
            name='travel_mode',
            field=models.ForeignKey(null=True, to='heritage.TravelMode', blank=True),
        ),
        migrations.AddField(
            model_name='culturalobservation',
            name='value_feature',
            field=models.ForeignKey(null=True, to='heritage.Feature', related_name='value', blank=True),
        ),
    ]

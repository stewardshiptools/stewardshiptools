# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import django_hstore.fields
from django.conf import settings
import model_utils.fields
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Confidentiality',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('confidential', models.BooleanField(default=True, verbose_name='Confidential?')),
                ('comments', models.TextField(blank=True, null=True)),
                ('release_signed', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='DublinCore',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contributor', models.TextField(blank=True, null=True, help_text='An entity responsible for making contributions to the resource.', verbose_name='Contributors')),
                ('coverage', models.TextField(blank=True, null=True, help_text='The spatial or temporal topic of the resource, the spatial applicability                            of the resource, or the jurisdiction under which the resource is relevant.', verbose_name='Coverage')),
                ('creator', models.TextField(blank=True, null=True, help_text='An entity primarily responsible for making the resource.', verbose_name='Creators')),
                ('date', models.DateField(blank=True, null=True, help_text='A point or period of time associated with an event in the lifecycle of the resource.', verbose_name='Date')),
                ('description', models.TextField(blank=True, null=True, help_text='An account of the resource.', verbose_name='Description')),
                ('format', models.TextField(blank=True, null=True, help_text='The file format, physical medium, or dimensions of the resource.', verbose_name='Format')),
                ('identifier', models.TextField(blank=True, null=True, help_text='An unambiguous reference to the resource within a given context.', verbose_name='Identifier')),
                ('language', models.TextField(blank=True, null=True, help_text='A language of the resource.', verbose_name='Language')),
                ('publisher', models.TextField(blank=True, null=True, help_text='An entity responsible for making the resource available.', verbose_name='Publishers')),
                ('relation', models.TextField(blank=True, null=True, help_text='A related resource.', verbose_name='Relation')),
                ('rights', models.TextField(blank=True, null=True, help_text='Information about rights held in and over the resource.', verbose_name='Rights')),
                ('source', models.TextField(blank=True, null=True, help_text='A related resource from which the described resource is derived.', verbose_name='Source')),
                ('subject', models.TextField(blank=True, null=True, help_text='The topic of the resource.', verbose_name='Subject')),
                ('title', models.TextField(blank=True, null=True, help_text='A name given to the resource.', verbose_name='Title')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Holdings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_type_comments', models.TextField(blank=True, null=True)),
                ('source_type', models.CharField(blank=True, max_length=250, null=True, help_text='Primary Source - A document or record containing first-hand information or original data on a topic; A work created at the time of an event or by a person who directly experienced an event; Some examples include: interviews, diaries, letters, journals, original hand-written manuscripts, newspaper and magazine clippings, government documents, etc. Secondary Source - Any published or unpublished work that is one step removed from the original source, usually describing, summarizing, analyzing, evaluating, derived from, or based on primary source materials; A source that is one step removed from the original event or experience; A source that provides criticism or interpretation of a primary source; Some examples include: textbooks, review articles, biographies, historical films, music and art, articles about people and events from the past.', choices=[('Primary', 'Primary'), ('Secondary', 'Secondary')])),
                ('media_mode', models.CharField(blank=True, max_length=250, null=True, help_text='Is the document a Physical (paper hardcopy) or Digital (scanned as PDF, Word Doc, Jpg, etc) or Both (you have it in its original state and as a digital file).', choices=[('Physical', 'Physical'), ('Digital', 'Digital'), ('Both', 'Both')])),
                ('item_internal_location', models.TextField(blank=True, null=True)),
                ('digital_file_name_path', models.CharField(blank=True, max_length=500, null=True, help_text='Enter the full file name and path for the document, for example if the file is stored on a shared drive. Example S://heritage/2010/project/documents/file_123_20100213.pdf')),
                ('digital_file_name', models.CharField(blank=True, max_length=500, null=True)),
                ('digital_file_ocrd', models.BooleanField(default=False)),
                ('digital_file_type_comments', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'Holdings',
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=250)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('extra_data', django_hstore.fields.DictionaryField(blank=True, null=True)),
                ('confidentiality', models.OneToOneField(to='library.Confidentiality', blank=True, null=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', blank=True, null=True)),
                ('dublin_core', models.OneToOneField(to='library.DublinCore')),
                ('holdings', models.OneToOneField(to='library.Holdings', blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ItemAssetRelation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('item', models.ForeignKey(to='library.Item')),
            ],
        ),
        migrations.CreateModel(
            name='ItemType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('description', models.TextField(blank=True, null=True)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(to='library.ItemType', blank=True, related_name='children', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MUPCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('weight', models.SmallIntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Relations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cataloger', models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, related_name='library_relations_cataloger_related', null=True)),
                ('related_items', models.ManyToManyField(blank=True, to='library.Item')),
                ('reviewer', models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, related_name='library_relations_reviewer_related', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ResearcherNotes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spreadsheet_id', models.PositiveIntegerField(blank=True, null=True)),
                ('researcher_notes', models.TextField(blank=True, null=True)),
                ('actions_needed', models.TextField(blank=True, null=True)),
                ('search_location', models.CharField(blank=True, max_length=500, null=True)),
                ('search_terms', models.CharField(blank=True, max_length=500, null=True)),
                ('search_results', models.CharField(blank=True, max_length=500, null=True)),
                ('search_identifier', models.CharField(blank=True, max_length=500, null=True)),
                ('cross_reference', models.CharField(blank=True, max_length=500, null=True)),
                ('search_summary', models.TextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('summary', models.TextField(blank=True, null=True)),
                ('people_mentioned', models.TextField(blank=True, null=True)),
                ('fn_people_mentioned', models.TextField(blank=True, null=True)),
                ('full_text', models.CharField(blank=True, max_length=500, null=True)),
                ('mup_category', models.ForeignKey(to='library.MUPCategory', blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UseAndOccupancyCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('weight', models.SmallIntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='review',
            name='use_occupancy_category',
            field=models.ForeignKey(to='library.UseAndOccupancyCategory', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='researcher_notes',
            field=models.OneToOneField(to='library.ResearcherNotes', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='review',
            field=models.OneToOneField(to='library.Review', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='dublincore',
            name='type',
            field=models.ForeignKey(to='library.ItemType', blank=True, null=True),
        ),
    ]

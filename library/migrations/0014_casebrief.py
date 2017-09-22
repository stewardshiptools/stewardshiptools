# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0001_initial'),
        ('crm', '0023_userpersonproxy'),
        ('library', '0013_auto_20170413_0736'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaseBrief',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('story_title', models.CharField(null=True, blank=True, max_length=500)),
                ('keywords', models.TextField(null=True, help_text='Words, names, places, etc. that you think should be highlighted.', verbose_name='Keyword(s)', blank=True)),
                ('source_notes', models.TextField(null=True, help_text='Notes describing where in the documents the story can be found.', verbose_name='Source Notes', blank=True)),
                ('issues', models.TextField(null=True, help_text='The main issue(s) or problem(s) that the story focuses on.', blank=True)),
                ('facts', models.TextField(null=True, help_text='Facts in the story that are relevant to understanding the issue(s) and their resolution. Who, What, When and Where? Use point form.', blank=True)),
                ('decision', models.TextField(null=True, help_text='What is decided or how is the issue finally addressed or resolved', verbose_name='Decision / Resolution', blank=True)),
                ('reasons', models.CharField(help_text='Describe the background to the Resolution using these categories: Said - A reason behind the decision or resolution that is stated or explained in the story; Unsaid - A reason behind the decision or resolution that is not directly stated or explained in the story,but that you interpret as a reason or explanation.', blank=True, choices=[('said', 'Said'), ('unsaid', 'Unsaid')], null=True, verbose_name='Reason(s)', max_length=50)),
                ('notes', models.TextField(null=True, help_text='General notes. Include anything that provides greater context to the story e.g. words, songs, dances, art, place names, etc. Include unanswered questions that require follow up.', blank=True)),
                ('cataloger', models.ForeignKey(to='crm.UserPersonProxy', on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True, related_name='library_casebrief_cataloger_related')),
                ('reviewer', models.ForeignKey(to='crm.UserPersonProxy', on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True, related_name='library_casebrief_reviewer_related')),
                ('sources', models.ManyToManyField(to='library.Item', help_text='Select the Item containing the digital version of the story cited.', verbose_name='Source(s)', blank=True)),
                ('tags', taggit.managers.TaggableManager(to='tags.Tag', through='tags.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags', blank=True)),
            ],
        ),
    ]

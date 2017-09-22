# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('library', '0029_auto_20170501_1312'),
    ]

    operations = [
        migrations.CreateModel(
            name='FirstNationsPersonMentionedTag',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name', unique=True)),
                ('slug', models.SlugField(max_length=100, verbose_name='Slug', unique=True)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'First Nations People Mentioned',
                'verbose_name': 'First Nations Person Mentioned',
            },
        ),
        migrations.CreateModel(
            name='FirstNationsPersonMentionedTaggedItem',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('object_id', models.IntegerField(verbose_name='Object id', db_index=True)),
                ('content_type', models.ForeignKey(related_name='library_firstnationspersonmentionedtaggeditem_tagged_items', to='contenttypes.ContentType', verbose_name='Content type')),
                ('tag', models.ForeignKey(related_name='library_firstnationspersonmentionedtaggeditem_items', to='library.FirstNationsPersonMentionedTag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='review',
            name='fn_people_mentioned',
            field=taggit.managers.TaggableManager(to='library.FirstNationsPersonMentionedTag', help_text='A comma-separated list of tags.', verbose_name='Tags', through='library.FirstNationsPersonMentionedTaggedItem', blank=True),
        ),
    ]

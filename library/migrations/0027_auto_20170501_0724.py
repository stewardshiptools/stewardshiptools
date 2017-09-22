# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tags.managers
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('ecosystems', '0007_auto_20170501_0647'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('library', '0026_auto_20170427_1426'),
    ]

    operations = [
        migrations.CreateModel(
            name='FirstNationsPersonMentionedTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(unique=True, verbose_name='Name', max_length=100)),
                ('slug', models.SlugField(unique=True, verbose_name='Slug', max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'First Nations People Mentioned',
                'verbose_name': 'First Nations Person Mentioned',
            },
        ),
        migrations.CreateModel(
            name='FirstNationsPersonMentionedTaggedItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.IntegerField(verbose_name='Object id', db_index=True)),
                ('content_type', models.ForeignKey(verbose_name='Content type', related_name='library_firstnationspersonmentionedtaggeditem_tagged_items', to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PersonMentionedTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(unique=True, verbose_name='Name', max_length=100)),
                ('slug', models.SlugField(unique=True, verbose_name='Slug', max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name_plural': 'People Mentioned',
                'verbose_name': 'Person Mentioned',
            },
        ),
        migrations.CreateModel(
            name='PersonMentionedTaggedItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.IntegerField(verbose_name='Object id', db_index=True)),
                ('content_type', models.ForeignKey(verbose_name='Content type', related_name='library_personmentionedtaggeditem_tagged_items', to='contenttypes.ContentType')),
                ('tag', models.ForeignKey(to='library.PersonMentionedTag', related_name='library_personmentionedtaggeditem_items')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='review',
            name='fn_people_mentioned',
        ),
        migrations.RemoveField(
            model_name='review',
            name='people_mentioned',
        ),
        migrations.AddField(
            model_name='review',
            name='animals',
            field=taggit.managers.TaggableManager(verbose_name='Tags', to='ecosystems.AnimalTag', help_text='A comma-separated list of tags.', blank=True, through='ecosystems.AnimalTaggedItem'),
        ),
        migrations.AddField(
            model_name='review',
            name='plants',
            field=taggit.managers.TaggableManager(verbose_name='Tags', to='ecosystems.PlantTag', help_text='A comma-separated list of tags.', blank=True, through='ecosystems.PlantTaggedItem'),
        ),
        migrations.AlterField(
            model_name='casebrief',
            name='keywords',
            field=tags.managers.TaggableManagerExtended(verbose_name='Tags', to='library.CaseBriefTag', help_text='Words, names, places, etc. that you think should be highlighted.', blank=True, through='library.CaseBriefTaggedItem'),
        ),
        migrations.AddField(
            model_name='firstnationspersonmentionedtaggeditem',
            name='tag',
            field=models.ForeignKey(to='library.PersonMentionedTag', related_name='library_firstnationspersonmentionedtaggeditem_items'),
        ),
    ]

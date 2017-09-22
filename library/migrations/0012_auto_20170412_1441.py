# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0011_auto_20170410_0737'),
    ]

    operations = [
        migrations.CreateModel(
            name='CollectionTag',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(verbose_name='Name', unique=True, max_length=100)),
                ('slug', models.SlugField(verbose_name='Slug', unique=True, max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Collection Tag',
                'verbose_name_plural': 'Collection Tags',
            },
        ),
        migrations.CreateModel(
            name='CollectionTaggedItem',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='item',
            name='cataloger',
            field=models.ForeignKey(to='crm.UserPersonProxy', on_delete=django.db.models.deletion.SET_NULL, blank=True, null=True, related_name='library_item_cataloger_related'),
        ),
        migrations.AlterField(
            model_name='item',
            name='reviewer',
            field=models.ForeignKey(to='crm.UserPersonProxy', on_delete=django.db.models.deletion.SET_NULL, blank=True, null=True, related_name='library_item_reviewer_related'),
        ),
        migrations.AddField(
            model_name='collectiontaggeditem',
            name='content_object',
            field=models.ForeignKey(to='library.Item'),
        ),
        migrations.AddField(
            model_name='collectiontaggeditem',
            name='tag',
            field=models.ForeignKey(to='library.CollectionTag', related_name='library_collectiontaggeditem_items'),
        ),
        migrations.AddField(
            model_name='item',
            name='collections',
            field=taggit.managers.TaggableManager(verbose_name='Tags', to='library.CollectionTag', help_text='A comma-separated list of tags.', through='library.CollectionTaggedItem', blank=True),
        ),
    ]

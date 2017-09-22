# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0015_auto_20170419_0720'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaseBriefTag',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Name')),
                ('slug', models.SlugField(max_length=100, unique=True, verbose_name='Slug')),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Case Brief Tag',
                'verbose_name_plural': 'Case Brief Tags',
            },
        ),
        migrations.CreateModel(
            name='CaseBriefTaggedItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('content_object', models.ForeignKey(to='library.CaseBrief')),
                ('tag', models.ForeignKey(to='library.CaseBriefTag', related_name='library_casebrieftaggeditem_items')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0071_auto_20161211_0613'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlternatePlaceName',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CommonPlaceName',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GazetteerNameTag',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=100, verbose_name='Name')),
                ('slug', models.SlugField(verbose_name='Slug', max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Gazetteer Name',
                'verbose_name_plural': 'Gazetteer Names',
            },
        ),
        migrations.CreateModel(
            name='GazetteerNameTaggedPlace',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('uuid', models.UUIDField(editable=False, default=uuid.uuid4)),
                ('name', models.CharField(max_length=200)),
                ('notes', models.TextField(blank=True, null=True)),
                ('gazetteer_names', taggit.managers.TaggableManager(through='heritage.GazetteerNameTaggedPlace', verbose_name='Tags', blank=True, to='heritage.GazetteerNameTag', help_text='A comma-separated list of tags.')),
            ],
        ),
        migrations.CreateModel(
            name='PlaceType',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('place_type', models.CharField(max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='place',
            name='place_types',
            field=models.ManyToManyField(to='heritage.PlaceType', blank=True),
        ),
        migrations.AddField(
            model_name='gazetteernametaggedplace',
            name='content_object',
            field=models.ForeignKey(to='heritage.Place'),
        ),
        migrations.AddField(
            model_name='gazetteernametaggedplace',
            name='tag',
            field=models.ForeignKey(related_name='heritage_gazetteernametaggedplace_items', to='heritage.GazetteerNameTag'),
        ),
        migrations.AddField(
            model_name='commonplacename',
            name='place',
            field=models.ForeignKey(to='heritage.Place'),
        ),
        migrations.AddField(
            model_name='alternateplacename',
            name='place',
            field=models.ForeignKey(to='heritage.Place'),
        ),
    ]

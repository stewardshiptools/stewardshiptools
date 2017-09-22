# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('ecosystems', '0006_planttag_planttaggeditem'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnimalTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(unique=True, verbose_name='Name', max_length=100)),
                ('slug', models.SlugField(unique=True, verbose_name='Slug', max_length=100)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Animal',
                'verbose_name_plural': 'Animals',
            },
        ),
        migrations.CreateModel(
            name='AnimalTaggedItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.IntegerField(db_index=True, verbose_name='Object id')),
                ('content_type', models.ForeignKey(verbose_name='Content type', to='contenttypes.ContentType', related_name='ecosystems_animaltaggeditem_tagged_items')),
                ('tag', models.ForeignKey(to='ecosystems.AnimalTag', related_name='ecosystems_animaltaggeditem_items')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='planttag',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
    ]

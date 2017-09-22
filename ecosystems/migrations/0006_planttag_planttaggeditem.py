# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('ecosystems', '0005_auto_20170501_0635'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlantTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(verbose_name='Name', unique=True, max_length=100)),
                ('slug', models.SlugField(unique=True, verbose_name='Slug', max_length=100)),
            ],
            options={
                'verbose_name': 'Plant',
                'verbose_name_plural': 'Plants',
            },
        ),
        migrations.CreateModel(
            name='PlantTaggedItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('object_id', models.IntegerField(db_index=True, verbose_name='Object id')),
                ('content_type', models.ForeignKey(verbose_name='Content type', related_name='ecosystems_planttaggeditem_tagged_items', to='contenttypes.ContentType')),
                ('tag', models.ForeignKey(related_name='ecosystems_planttaggeditem_items', to='ecosystems.PlantTag')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecosystems', '0007_auto_20170501_0647'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommonAnimalName',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=200)),
                ('animal', models.ForeignKey(to='ecosystems.AnimalTag', related_name='common_names')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CommonPlantName',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=200)),
                ('plant', models.ForeignKey(to='ecosystems.PlantTag', related_name='common_names')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='IndigenousAnimalName',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=200)),
                ('animal', models.ForeignKey(to='ecosystems.AnimalTag', related_name='indigenous_names')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='IndigenousPlantName',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=200)),
                ('plant', models.ForeignKey(to='ecosystems.PlantTag', related_name='indigenous_names')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

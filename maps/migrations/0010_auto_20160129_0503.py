# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0009_auto_20160127_0109'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeafletOverlayLayer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(help_text='The name that will be shown to the user in layers switches, etc.', max_length=100)),
                ('machine_name', models.CharField(unique=True, help_text='Must be unique and comprised of letters, numbers, dashes, and underscores', max_length=100)),
                ('description', models.TextField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='leafletmap',
            name='overlay_layers',
            field=models.CharField(null=True, blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='leafletmap',
            name='default_center_lat',
            field=models.FloatField(default=54.9),
        ),
        migrations.AlterField(
            model_name='leafletmap',
            name='default_center_lon',
            field=models.FloatField(default=-128),
        ),
        migrations.AlterField(
            model_name='leafletmap',
            name='default_initial_zoom',
            field=models.PositiveSmallIntegerField(default=4),
        ),
    ]

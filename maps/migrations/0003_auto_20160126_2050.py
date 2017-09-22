# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0002_auto_20160126_2036'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeafletTileLayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('url_template', models.CharField(max_length=1000)),
                ('attribution', models.CharField(blank=True, null=True, max_length=100)),
                ('max_zoom', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('sub_domains', models.CharField(default='abc', max_length=200, help_text='Subdomains of the tile service. Can be passed in the form of one string(where each letter is a subdomain name) or a comma separated list ofstrings.')),
            ],
        ),
        migrations.DeleteModel(
            name='LeafletBaseLayer',
        ),
        migrations.AlterField(
            model_name='leafletmap',
            name='base_layers',
            field=models.ManyToManyField(to='maps.LeafletTileLayer'),
        ),
    ]

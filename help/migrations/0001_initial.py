# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HelpText',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=50)),
                ('html', models.TextField(null=True, blank=True)),
                ('note', models.TextField(null=True, blank=True, verbose_name='Note on this help text.')),
            ],
        ),
        migrations.CreateModel(
            name='PageHelp',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('page_id', models.CharField(max_length=50, unique=True)),
                ('title', models.CharField(max_length=100)),
                ('helptext', models.ManyToManyField(to='help.HelpText', blank=True)),
            ],
        ),
    ]

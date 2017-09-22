# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0044_record_session'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecordSessionLink',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('page_number', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('line_number', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('original_comment_on_map', models.CharField(blank=True, null=True, max_length=200)),
                ('transcript_excerpt', models.CharField(blank=True, null=True, max_length=200)),
                ('transcript_excerpt_san', models.CharField(blank=True, null=True, max_length=200)),
                ('record', models.ForeignKey(to='heritage.Record')),
                ('session', models.ForeignKey(to='heritage.Session')),
            ],
        ),
    ]

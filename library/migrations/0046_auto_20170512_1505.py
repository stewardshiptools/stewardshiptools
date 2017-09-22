# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('library', '0045_auto_20170510_1422'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='casebrief',
            name='is_removed',
        ),
        migrations.RemoveField(
            model_name='casebrieftag',
            name='is_removed',
        ),
        migrations.RemoveField(
            model_name='collectiontag',
            name='is_removed',
        ),
        migrations.RemoveField(
            model_name='dublincore',
            name='is_removed',
        ),
        migrations.RemoveField(
            model_name='holdings',
            name='is_removed',
        ),
        migrations.RemoveField(
            model_name='item',
            name='is_removed',
        ),
        migrations.RemoveField(
            model_name='researchernotes',
            name='is_removed',
        ),
        migrations.RemoveField(
            model_name='synthesis',
            name='is_removed',
        ),
        migrations.RemoveField(
            model_name='synthesisitem',
            name='is_removed',
        ),
    ]

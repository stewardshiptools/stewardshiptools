# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0001_initial'),
        ('library', '0007_auto_20170309_1201'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='tags',
            field=taggit.managers.TaggableManager(verbose_name='Tags', help_text='A comma-separated list of tags.', to='tags.Tag', through='tags.TaggedItem'),
        ),
    ]

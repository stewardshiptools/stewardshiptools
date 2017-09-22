# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0008_item_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='tags',
            field=taggit.managers.TaggableManager(verbose_name='Tags', blank=True, to='tags.Tag', help_text='A comma-separated list of tags.', through='tags.TaggedItem'),
        ),
    ]

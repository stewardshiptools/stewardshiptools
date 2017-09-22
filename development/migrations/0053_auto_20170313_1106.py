# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0052_developmentproject_tags'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProjectTag',
        ),
        migrations.AlterField(
            model_name='developmentproject',
            name='tags',
            field=taggit.managers.TaggableManager(verbose_name='Tags', blank=True, help_text='A comma-separated list of tags.', to='tags.Tag', through='tags.TaggedItem'),
        ),
    ]

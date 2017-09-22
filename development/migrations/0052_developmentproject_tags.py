# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('tags', '0001_initial'),
        ('development', '0051_remove_developmentproject_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='developmentproject',
            name='tags',
            field=taggit.managers.TaggableManager(through='tags.TaggedItem', help_text='A comma-separated list of tags.', to='tags.Tag', verbose_name='Tags'),
        ),
    ]

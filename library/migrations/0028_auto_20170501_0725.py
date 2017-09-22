# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0027_auto_20170501_0724'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='fn_people_mentioned',
            field=taggit.managers.TaggableManager(to='library.PersonMentionedTag', help_text='A comma-separated list of tags.', through='library.FirstNationsPersonMentionedTaggedItem', verbose_name='Tags', blank=True),
        ),
        migrations.AddField(
            model_name='review',
            name='people_mentioned',
            field=taggit.managers.TaggableManager(to='library.PersonMentionedTag', help_text='A comma-separated list of tags.', through='library.PersonMentionedTaggedItem', verbose_name='Tags', blank=True),
        ),
    ]

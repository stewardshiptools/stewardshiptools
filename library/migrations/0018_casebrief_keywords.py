# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0017_auto_20170420_0617'),
    ]

    operations = [
        migrations.AddField(
            model_name='casebrief',
            name='keywords',
            field=taggit.managers.TaggableManager(blank=True, to='library.CaseBriefTag', help_text='Words, names, places, etc. that you think should be highlighted.', through='library.CaseBriefTaggedItem', verbose_name='Tags'),
        ),
    ]

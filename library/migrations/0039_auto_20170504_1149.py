# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0038_auto_20170502_1211'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='firstnationspersonmentionedtaggeditem',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='firstnationspersonmentionedtaggeditem',
            name='tag',
        ),
        migrations.RemoveField(
            model_name='review',
            name='fn_people_mentioned',
        ),
        migrations.DeleteModel(
            name='FirstNationsPersonMentionedTag',
        ),
        migrations.DeleteModel(
            name='FirstNationsPersonMentionedTaggedItem',
        ),
    ]

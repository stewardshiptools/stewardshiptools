# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0028_auto_20170501_0725'),
    ]

    operations = [
        migrations.DeleteModel(
            name='FirstNationsPersonMentionedTag',
        ),
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
            name='FirstNationsPersonMentionedTaggedItem',
        ),
    ]

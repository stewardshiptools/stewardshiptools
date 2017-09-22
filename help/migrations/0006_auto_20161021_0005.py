# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('help', '0005_pagehelp_tooltip'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='helptext',
            options={'verbose_name': 'help doc', 'ordering': ['title']},
        ),
        migrations.AlterModelOptions(
            name='pagehelp',
            options={'verbose_name': 'Help doc assignment'},
        ),
    ]

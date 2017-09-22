# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0053_auto_20160620_2339'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recordsessionlink',
            name='transcript_excerpt_san',
        ),
    ]

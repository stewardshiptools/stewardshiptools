# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0045_recordsessionlink'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recordsessionlink',
            name='transcript_excerpt',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='recordsessionlink',
            name='transcript_excerpt_san',
            field=models.TextField(blank=True, null=True),
        ),
    ]

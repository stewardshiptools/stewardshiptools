# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0054_remove_recordsessionlink_transcript_excerpt_san'),
    ]

    operations = [
        migrations.AddField(
            model_name='recordsessionlink',
            name='transcript_excerpt_full',
            field=models.TextField(blank=True, null=True, help_text='This is the transcript text usedabove,with surrounding lines forcontext.'),
        ),
        migrations.AlterField(
            model_name='recordsessionlink',
            name='transcript_excerpt',
            field=models.TextField(blank=True, null=True, help_text='This is the transcript text that the recordwas created for.'),
        ),
    ]

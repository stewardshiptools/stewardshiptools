# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0034_auto_20170502_0721'),
    ]

    operations = [
        migrations.AlterField(
            model_name='casebrief',
            name='reasons_notes',
            field=models.TextField(blank=True, verbose_name='Reason(s)', help_text='Describe the background to the Resolution using these categories: Said - A reason behind the decision or resolution that is stated or explained in the story; Unsaid - A reason behind the decision or resolution that is not directly stated or explained in the story, but that you interpret as a reason or explanation.', null=True),
        ),
    ]

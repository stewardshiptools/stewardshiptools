# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0033_casebrief_reasons_notes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='casebrief',
            name='reasons',
        ),
        migrations.AlterField(
            model_name='casebrief',
            name='reasons_notes',
            field=models.TextField(null=True, blank=True, verbose_name='Describe the background to the Resolution using these categories: Said - A reason behind the decision or resolution that is stated or explained in the story; Unsaid - A reason behind the decision or resolution that is not directly stated or explained in the story,but that you interpret as a reason or explanation.'),
        ),
    ]

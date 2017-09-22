# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0032_auto_20170502_0132'),
    ]

    operations = [
        migrations.AddField(
            model_name='casebrief',
            name='reasons_notes',
            field=models.TextField(verbose_name='Explanation for selected reason', null=True, blank=True),
        ),
    ]

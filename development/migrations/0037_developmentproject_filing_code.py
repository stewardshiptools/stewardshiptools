# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0036_filingcode'),
    ]

    operations = [
        migrations.AddField(
            model_name='developmentproject',
            name='filing_code',
            field=mptt.fields.TreeForeignKey(blank=True, to='development.FilingCode', null=True),
        ),
    ]

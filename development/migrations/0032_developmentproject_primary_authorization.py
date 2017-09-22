# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0031_developmentproject_highlight'),
    ]

    operations = [
        migrations.AddField(
            model_name='developmentproject',
            name='primary_authorization',
            field=models.CharField(choices=[['a', 'Test'], ['b', 'Lists']], max_length=200, null=True, blank=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0032_developmentproject_primary_authorization'),
    ]

    operations = [
        migrations.AddField(
            model_name='developmentproject',
            name='area',
            field=models.CharField(max_length=200, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='developmentproject',
            name='rationale',
            field=models.TextField(verbose_name='Rationale', blank=True),
        ),
        migrations.AlterField(
            model_name='developmentproject',
            name='primary_authorization',
            field=models.CharField(max_length=200, blank=True, null=True),
        ),
    ]

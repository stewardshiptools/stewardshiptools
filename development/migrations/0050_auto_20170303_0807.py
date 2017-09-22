# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0049_auto_20170120_0708'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileno',
            name='org_type',
            field=models.CharField(max_length=30, choices=[('government', 'Government'), ('proponent', 'Proponent'), ('other', 'Other')]),
        ),
    ]

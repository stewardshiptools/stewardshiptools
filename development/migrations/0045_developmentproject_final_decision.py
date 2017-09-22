# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0044_developmentaction_developmentprojectaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='developmentproject',
            name='final_decision',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Recommended'), ('rejected', 'Not Recommended')], default='pending', max_length=100),
        ),
    ]

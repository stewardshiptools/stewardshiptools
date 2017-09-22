# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0059_auto_20170619_1150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='developmentproject',
            name='consultation_stage',
            field=models.ForeignKey(to='development.ConsultationStage', blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]

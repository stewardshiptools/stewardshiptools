# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0050_auto_20170303_0807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='developmentproject',
            name='consultation_stage',
            field=models.ForeignKey(to='development.ConsultationStage', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]

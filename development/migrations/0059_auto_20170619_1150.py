# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0058_delete_projectgroup'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='developmentasset',
            options={'verbose_name': 'Develoment File'},
        ),
        migrations.AlterModelOptions(
            name='developmentprojectasset',
            options={'verbose_name': 'Development Project File'},
        ),
        migrations.AlterField(
            model_name='developmentproject',
            name='consultation_stage',
            field=models.ForeignKey(blank=True, null=True, to='development.ConsultationStage', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]

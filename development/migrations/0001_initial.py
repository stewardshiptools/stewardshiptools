# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ConsultationStage',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('stage_name', models.CharField(max_length=150, verbose_name='Consultation stage name')),
            ],
        ),
        migrations.CreateModel(
            name='DevelopmentProject',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('cedar_project_name', models.CharField(max_length=80)),
                ('cedar_project_number', models.IntegerField(verbose_name='Cedar project number')),
                ('cedar_comm_code', models.CharField(max_length=80, blank=True, null=True)),
                ('govt_project_code', models.CharField(max_length=80, blank=True, null=True)),
                ('initial_date',
                 models.DateField(verbose_name='Initial Contact Date', help_text='Date on which first contact was made.', blank=True, null=True)),
                ('consultation_stage', models.ForeignKey(to='development.ConsultationStage')),
            ],
        ),
    ]

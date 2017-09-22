# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('development', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('tag', models.CharField(verbose_name='Tag text', max_length=30)),
            ],
        ),
        migrations.AlterField(
            model_name='developmentproject',
            name='cedar_comm_code',
            field=models.CharField(verbose_name='Cedar communication code', null=True, max_length=80, blank=True),
        ),
        migrations.AddField(
            model_name='developmentproject',
            name='project_tag',
            field=models.ManyToManyField(to='development.ProjectTag'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecosystems', '0003_auto_20170110_1159'),
    ]

    operations = [
        migrations.AddField(
            model_name='ecosystemsgislayer',
            name='project',
            field=models.ForeignKey(null=True, to='ecosystems.EcosystemsProject', blank=True),
        ),
        migrations.AlterField(
            model_name='ecosystemsproject',
            name='description',
            field=models.TextField(null=True, help_text='Short description of the project.', verbose_name='Description', blank=True),
        ),
        migrations.AlterField(
            model_name='ecosystemsproject',
            name='end_date',
            field=models.DateField(null=True, verbose_name='Project End Date', blank=True),
        ),
        migrations.AlterField(
            model_name='ecosystemsproject',
            name='start_date',
            field=models.DateField(null=True, verbose_name='Project Start Date', blank=True),
        ),
    ]

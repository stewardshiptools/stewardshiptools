# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0060_project_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='phase_code',
            field=models.CharField(help_text='Project phase code.', null=True, blank=True, verbose_name='Phase code', max_length=8),
        ),
        migrations.AlterField(
            model_name='project',
            name='picture',
            field=models.ImageField(null=True, upload_to='heritage', blank=True),
        ),
    ]

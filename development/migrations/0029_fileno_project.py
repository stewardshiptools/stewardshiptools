# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0028_remove_developmentproject_external_file_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileno',
            name='project',
            field=models.ForeignKey(default=1, to='development.DevelopmentProject'),
            preserve_default=False,
        ),
    ]

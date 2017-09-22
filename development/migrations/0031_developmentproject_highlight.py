# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0030_remove_developmentproject_govt_project_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='developmentproject',
            name='highlight',
            field=models.BooleanField(default=False),
        ),
    ]

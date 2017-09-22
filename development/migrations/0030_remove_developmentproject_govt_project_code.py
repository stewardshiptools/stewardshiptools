# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0029_fileno_project'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='developmentproject',
            name='govt_project_code',
        ),
    ]

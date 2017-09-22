# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0057_remove_developmentproject_project_group'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ProjectGroup',
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0037_developmentproject_filing_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='developmentproject',
            name='cedar_project_code',
        ),
    ]

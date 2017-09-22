# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0046_developmentproject_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='developmentproject',
            name='cedar_project_name',
            field=models.CharField(max_length=250),
        ),
    ]

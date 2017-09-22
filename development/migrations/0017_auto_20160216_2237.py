# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('development', '0016_developmentproject_cedar_project_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='developmentproject',
            name='cedar_project_code',
            field=models.CharField(verbose_name='Cedar project code', default=1, unique=True, max_length=80),
            preserve_default=False,
        ),
    ]

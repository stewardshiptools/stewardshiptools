# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('development', '0022_auto_20160729_2239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='developmentproject',
            name='external_file_no',
            field=models.ManyToManyField(to='development.FileNo', blank=True),
        ),
    ]

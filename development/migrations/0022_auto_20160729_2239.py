# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('development', '0021_auto_20160729_2237'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='developmentproject',
            name='external_file_no',
        ),
        migrations.AddField(
            model_name='developmentproject',
            name='external_file_no',
            field=models.ManyToManyField(blank=True, to='development.FileNo', null=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

'''
Migration 0023, 0024, and 0025 form 3 parts of custom migration
to remove asset inheritance on messageattachment model.
Needed a new ID pk field but it had to be added as null=True,
calculated (0024) and then set to PK and null=False (0025)
'''


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0024_auto_20161026_1505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messageattachment',
            name='id',
            field=models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', null=False, serialize=False),
            preserve_default=False,
        ),
    ]

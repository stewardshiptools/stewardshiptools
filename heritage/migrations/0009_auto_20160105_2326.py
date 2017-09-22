# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0008_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='species',
            name='name_equivalents',
            field=models.CharField(blank=True, verbose_name='Name equivalents', max_length=100),
        ),
    ]

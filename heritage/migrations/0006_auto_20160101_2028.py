# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0005_auto_20160101_1903'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='session',
            unique_together=set([('interview', 'number')]),
        ),
    ]

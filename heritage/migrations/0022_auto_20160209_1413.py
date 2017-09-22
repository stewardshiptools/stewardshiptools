# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('heritage', '0021_auto_20160209_1354'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='interview',
            options={'permissions': (('view_interview', 'Can view interview'),)},
        ),
        migrations.AlterModelOptions(
            name='session',
            options={'permissions': (('view_session', 'Can view session'),)},
        ),
    ]

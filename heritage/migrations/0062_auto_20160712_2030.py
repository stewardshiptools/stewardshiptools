# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0061_auto_20160712_2014'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={'ordering': ('start_date', 'end_date', 'name'), 'permissions': (('view_project', 'Can view project'),)},
        ),
    ]

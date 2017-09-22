# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0002_auto_20170306_2332'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Relations',
        ),
    ]

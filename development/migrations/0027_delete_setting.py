# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('development', '0026_auto_20160804_2048'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Setting',
        ),
    ]

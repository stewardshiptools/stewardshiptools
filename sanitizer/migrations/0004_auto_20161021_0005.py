# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sanitizer', '0003_auto_20160623_2135'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='relatedsensitivephrase',
            options={'ordering': ('-id', 'phrase')},
        ),
        migrations.AlterModelOptions(
            name='sensitivephrase',
            options={'ordering': ('-id', 'phrase')},
        ),
    ]

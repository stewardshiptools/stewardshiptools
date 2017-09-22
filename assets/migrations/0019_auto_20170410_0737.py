# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0018_merge'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='asset',
            options={'ordering': ('-modified',)},
        ),
        migrations.AlterModelOptions(
            name='secureasset',
            options={'ordering': ('-modified',), 'permissions': (('view_secureasset', 'Can view secure asset'),)},
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecosystems', '0004_auto_20170111_0550'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ecosystemsasset',
            options={'verbose_name': 'Ecosystems File'},
        ),
        migrations.AlterModelOptions(
            name='ecosystemsprojectasset',
            options={'verbose_name': 'Ecosystems Project File'},
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0016_harvesthistory_last_harvest'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='harvestcodeprefix',
            options={'verbose_name_plural': 'Harvest code prefixes'},
        ),
        migrations.AlterModelOptions(
            name='harvesthistory',
            options={'verbose_name_plural': 'harvest histories', 'ordering': ['-last_harvest']},
        ),
        migrations.RemoveField(
            model_name='harvestcodeprefix',
            name='mailboxes',
        ),
    ]

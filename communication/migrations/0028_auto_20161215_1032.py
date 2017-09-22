# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0027_letter'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mailaccount',
            options={'permissions': (('harvest_mail_account', 'Can run mailharvest on mail account'),)},
        ),
    ]

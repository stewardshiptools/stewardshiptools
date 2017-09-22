# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0018_auto_20161019_0034'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mailbox',
            options={'verbose_name_plural': 'Mailboxes', 'permissions': (('harvest_mailbox', 'Can run mailharvest on mailbox'),)},
        ),
    ]

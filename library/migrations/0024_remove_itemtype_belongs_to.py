# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0023_item_belongs_to'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='itemtype',
            name='belongs_to',
        ),
    ]

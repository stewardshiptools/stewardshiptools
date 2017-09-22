# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('library', '0043_auto_20170510_1300'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='related_items',
            field=models.ManyToManyField(blank=True, related_name='_item_related_items_+', to='library.Item'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0073_auto_20170501_0803'),
        ('library', '0030_auto_20170501_1313'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='places_mentioned',
            field=models.ManyToManyField(related_name='item_reviews', to='heritage.Place', blank=True),
        ),
    ]

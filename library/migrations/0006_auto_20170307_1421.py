# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0005_auto_20170307_1419'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='files',
            field=models.ManyToManyField(through='library.ItemAssetRelation', blank=True, to='assets.SecureAsset'),
        ),
    ]

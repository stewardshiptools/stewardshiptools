# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0004_auto_20170307_1402'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='files',
            field=models.ManyToManyField(to='assets.SecureAsset', null=True, through='library.ItemAssetRelation'),
        ),
    ]

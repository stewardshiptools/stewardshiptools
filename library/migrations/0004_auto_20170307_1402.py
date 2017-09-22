# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0017_auto_20170307_1402'),
        ('library', '0003_delete_relations'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='itemassetrelation',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='itemassetrelation',
            name='object_id',
        ),
        migrations.AddField(
            model_name='item',
            name='files',
            field=models.ManyToManyField(through='library.ItemAssetRelation', to='assets.SecureAsset'),
        ),
        migrations.AddField(
            model_name='itemassetrelation',
            name='secureasset',
            field=models.ForeignKey(to='assets.SecureAsset', default=1),
            preserve_default=False,
        ),
    ]

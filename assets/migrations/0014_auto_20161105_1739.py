# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0013_metadocumentasset_metadocumentsecureasset'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metadocumentasset',
            name='asset',
            field=models.OneToOneField(to='assets.Asset', null=True, related_name='meta_document'),
        ),
        migrations.AlterField(
            model_name='metadocumentsecureasset',
            name='asset',
            field=models.OneToOneField(to='assets.SecureAsset', null=True, related_name='meta_document'),
        ),
    ]

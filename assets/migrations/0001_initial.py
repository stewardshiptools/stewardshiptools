# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import assets.asset_helpers
import django.core.files.storage


class Migration(migrations.Migration):
    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
                name='Asset',
                fields=[
                    ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                    ('name', models.CharField(null=True, max_length=100, blank=True)),
                    ('delete_file_with_record',
                     models.BooleanField(default=True, help_text='This will delete the file if this asset is deleted')),
                    ('file', models.FileField(upload_to=assets.asset_helpers.generate_asset_file_name)),
                ],
                options={
                    'abstract': False,
                },
        ),
        migrations.CreateModel(
                name='AssetType',
                fields=[
                    ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                    ('type_of_asset', models.CharField(max_length=30)),
                ],
        ),
        migrations.CreateModel(
                name='SecureAsset',
                fields=[
                    ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                    ('name', models.CharField(null=True, max_length=100, blank=True)),
                    ('delete_file_with_record',
                     models.BooleanField(default=True, help_text='This will delete the file if this asset is deleted')),
                    ('file', models.FileField(upload_to=assets.asset_helpers.generate_asset_file_name,
                                              storage=django.core.files.storage.FileSystemStorage(
                                                  base_url='/secure_asset',
                                                  location='/home/geomemes/cedar_media_secure'))),
                    ('asset_type', models.ForeignKey(to='assets.AssetType')),
                ],
                options={
                    'abstract': False,
                },
        ),
        migrations.AddField(
                model_name='asset',
                name='asset_type',
                field=models.ForeignKey(to='assets.AssetType'),
        ),
    ]

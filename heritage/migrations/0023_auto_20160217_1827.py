# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('assets', '0001_initial'),
        ('heritage', '0022_auto_20160209_1413'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeritageAsset',
            fields=[
                ('secureasset_ptr',
                 models.OneToOneField(parent_link=True, primary_key=True, to='assets.SecureAsset', auto_created=True, serialize=False)),
            ],
            options={
                'abstract': False,
            },
            bases=('assets.secureasset',),
        ),
        migrations.RemoveField(
            model_name='projectasset',
            name='secureasset_ptr',
        ),
        migrations.AddField(
            model_name='projectasset',
            name='heritageasset_ptr',
            field=models.OneToOneField(parent_link=True, primary_key=True, default=1, to='heritage.HeritageAsset', auto_created=True,
                                       serialize=False),
            preserve_default=False,
        ),
    ]

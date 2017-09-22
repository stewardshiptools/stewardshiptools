# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('heritage', '0035_auto_20160223_1446'),
    ]

    operations = [
        migrations.CreateModel(
            name='SessionAsset',
            fields=[
                ('heritageasset_ptr',
                 models.OneToOneField(primary_key=True, auto_created=True, serialize=False, parent_link=True, to='heritage.HeritageAsset')),
                ('session', models.ForeignKey(to='heritage.Session')),
            ],
            options={
                'abstract': False,
            },
            bases=('heritage.heritageasset',),
        ),
    ]

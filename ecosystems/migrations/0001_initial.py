# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0015_auto_20161105_1800'),
    ]

    operations = [
        migrations.CreateModel(
            name='EcosystemsAsset',
            fields=[
                ('secureasset_ptr', models.OneToOneField(auto_created=True, serialize=False, primary_key=True, to='assets.SecureAsset', parent_link=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('assets.secureasset',),
        ),
    ]

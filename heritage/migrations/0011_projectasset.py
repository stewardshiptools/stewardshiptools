# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '__first__'),
        ('heritage', '0010_auto_20160114_2146'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectAsset',
            fields=[
                ('secureasset_ptr', models.OneToOneField(serialize=False, to='assets.SecureAsset', primary_key=True, parent_link=True, auto_created=True)),
                ('project', models.ForeignKey(to='heritage.Project')),
            ],
            options={
                'abstract': False,
            },
            bases=('assets.secureasset',),
        ),
    ]

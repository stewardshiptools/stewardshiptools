# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('assets', '0002_auto_20160211_2003'),
        ('development', '0017_auto_20160216_2237'),
    ]

    operations = [
        migrations.CreateModel(
            name='DevelopmentAsset',
            fields=[
                ('secureasset_ptr',
                 models.OneToOneField(parent_link=True, primary_key=True, serialize=False, auto_created=True, to='assets.SecureAsset')),
            ],
            options={
                'abstract': False,
            },
            bases=('assets.secureasset',),
        ),
        migrations.CreateModel(
            name='DevelopmentProjectAsset',
            fields=[
                ('developmentasset_ptr',
                 models.OneToOneField(parent_link=True, primary_key=True, serialize=False, auto_created=True, to='development.DevelopmentAsset')),
                ('project', models.ForeignKey(to='development.DevelopmentProject')),
            ],
            options={
                'abstract': False,
            },
            bases=('development.developmentasset',),
        ),
    ]

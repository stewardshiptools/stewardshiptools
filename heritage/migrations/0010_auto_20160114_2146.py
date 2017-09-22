# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '__first__'),
        ('heritage', '0009_auto_20160105_2326'),
    ]

    operations = [
        migrations.CreateModel(
            name='InterviewAsset',
            fields=[
                ('secureasset_ptr', models.OneToOneField(auto_created=True, parent_link=True, serialize=False, primary_key=True, to='assets.SecureAsset')),
            ],
            options={
                'abstract': False,
            },
            bases=('assets.secureasset',),
        ),
        migrations.AlterModelOptions(
            name='ecologicalvalue',
            options={'ordering': ['description']},
        ),
        migrations.AlterModelOptions(
            name='fishingmethod',
            options={'ordering': ['description']},
        ),
        migrations.AlterModelOptions(
            name='harvestmethod',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='species',
            options={'ordering': ['description']},
        ),
        migrations.AlterModelOptions(
            name='speciestheme',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='timeframe',
            options={'ordering': ['description']},
        ),
        migrations.AlterModelOptions(
            name='use',
            options={'ordering': ['description']},
        ),
        migrations.CreateModel(
            name='SessionAsset',
            fields=[
                ('interviewasset_ptr', models.OneToOneField(auto_created=True, parent_link=True, serialize=False, primary_key=True, to='heritage.InterviewAsset')),
                ('session', models.ForeignKey(to='heritage.Session')),
            ],
            options={
                'abstract': False,
            },
            bases=('heritage.interviewasset',),
        ),
        migrations.AddField(
            model_name='interviewasset',
            name='interview',
            field=models.ForeignKey(to='heritage.Interview'),
        ),
    ]

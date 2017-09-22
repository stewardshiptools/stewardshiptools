# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('assets', '0010_auto_20160616_1957'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assettype',
            options={'ordering': ('type_of_asset',)},
        ),
        migrations.AddField(
            model_name='assettype',
            name='description',
            field=models.CharField(max_length=150, blank=True, null=True),
        ),
    ]

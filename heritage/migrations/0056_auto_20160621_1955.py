# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0055_auto_20160621_1944'),
    ]

    operations = [
        migrations.AddField(
            model_name='recordsessionlink',
            name='comment_number',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='recordsessionlink',
            name='spatial_code',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]

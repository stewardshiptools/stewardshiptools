# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0012_auto_20170412_1441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='full_text',
            field=models.TextField(blank=True, null=True),
        ),
    ]

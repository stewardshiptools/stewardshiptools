# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('communication', '0005_auto_20160818_1306'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='subject',
            field=models.CharField(max_length=255, verbose_name='Subject', default='subject'),
            preserve_default=False,
        ),
    ]

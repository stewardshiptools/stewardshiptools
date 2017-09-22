# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0012_auto_20160107_0107'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='interview',
            field=models.ForeignKey(to='heritage.Interview', default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='asset',
            name='session',
            field=models.ForeignKey(null=True, blank=True, to='heritage.Session'),
        ),
    ]

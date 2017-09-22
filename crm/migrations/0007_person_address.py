# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('crm', '0006_auto_20160310_1917'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='address',
            field=models.CharField(blank=True, verbose_name='Address', max_length=250, null=True),
        ),
    ]

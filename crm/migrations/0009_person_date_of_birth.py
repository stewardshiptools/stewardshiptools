# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('crm', '0008_auto_20160310_1958'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='date_of_birth',
            field=models.DateField(blank=True, verbose_name='Date of Birth', null=True),
        ),
    ]

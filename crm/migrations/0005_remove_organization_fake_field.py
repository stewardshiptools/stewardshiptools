# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('crm', '0004_auto_20160202_1146'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='fake_field',
        ),
    ]

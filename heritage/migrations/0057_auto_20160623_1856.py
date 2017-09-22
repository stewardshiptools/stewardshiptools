# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('heritage', '0056_auto_20160621_1955'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='interview',
            options={'permissions': (('view_interview', 'Can view interview'), ('view_sensitive_interview_data', 'Can view sensitive interview data'))},
        ),
    ]

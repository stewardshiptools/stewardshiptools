# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('communication', '0006_message_subject'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='communicationrelation',
            name='comm',
        ),
        migrations.RemoveField(
            model_name='communicationrelation',
            name='comm_type_ct',
        ),
        migrations.RemoveField(
            model_name='communicationrelation',
            name='comm_type_oid',
        ),
    ]

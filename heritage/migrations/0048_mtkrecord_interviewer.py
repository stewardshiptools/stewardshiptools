# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0004_auto_20160202_1146'),
        ('heritage', '0047_remove_mtkrecord_interviewer_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='mtkrecord',
            name='interviewer',
            field=models.ForeignKey(to='crm.Person', null=True, blank=True),
        ),
    ]

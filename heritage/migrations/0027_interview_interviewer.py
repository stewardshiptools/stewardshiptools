# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0004_auto_20160202_1146'),
        ('heritage', '0026_auto_20160217_2338'),
    ]

    operations = [
        migrations.AddField(
            model_name='interview',
            name='interviewer',
            field=models.ForeignKey(blank=True, to='crm.Person', related_name='interviews_conducted', null=True),
        ),
    ]

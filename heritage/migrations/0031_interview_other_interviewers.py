# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0004_auto_20160202_1146'),
        ('heritage', '0030_auto_20160219_0737'),
    ]

    operations = [
        migrations.AddField(
            model_name='interview',
            name='other_interviewers',
            field=models.ManyToManyField(related_name='interviews_assisted', to='crm.Person'),
        ),
    ]

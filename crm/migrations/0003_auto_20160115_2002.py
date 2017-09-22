# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0002_person_pic'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='role',
            options={'ordering': ('name',)},
        ),
    ]

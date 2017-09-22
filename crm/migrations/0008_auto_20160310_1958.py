# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('crm', '0007_person_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='address',
            field=models.TextField(max_length=250, blank=True, verbose_name='Address', null=True),
        ),
    ]

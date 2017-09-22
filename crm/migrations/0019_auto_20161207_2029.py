# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0018_auto_20161207_0536'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(verbose_name='Phone', blank=True, null=True, max_length=128),
        ),
    ]

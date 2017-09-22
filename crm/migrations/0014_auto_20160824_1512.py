# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import cedar.fields


class Migration(migrations.Migration):
    dependencies = [
        ('crm', '0013_role_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=cedar.fields.StrippedCharField(max_length=100, verbose_name='Name'),
        ),
    ]

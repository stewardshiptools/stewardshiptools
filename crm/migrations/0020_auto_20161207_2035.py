# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import cedar.fields


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0019_auto_20161207_2029'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='clan_family',
            field=cedar.fields.StrippedCharField(blank=True, max_length=100, verbose_name='Clan/Family', null=True),
        ),
    ]

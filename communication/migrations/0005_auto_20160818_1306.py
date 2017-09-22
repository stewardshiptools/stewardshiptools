# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('communication', '0004_auto_20160818_1253'),
    ]

    operations = [
        migrations.RenameField(
            model_name='communication',
            old_name='from_contact',
            new_name='from_contacts',
        ),
        migrations.RenameField(
            model_name='communication',
            old_name='to_contact',
            new_name='to_contacts',
        ),
    ]

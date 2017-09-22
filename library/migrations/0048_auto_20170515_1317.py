# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('library', '0047_auto_20170515_1313'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mupcategory',
            options={'verbose_name_plural': 'MUP Categories'},
        ),
    ]
